import asyncio
import logging
import os
import re
from typing import Any, Dict, List, Optional
from openai import OpenAI
import logging

import aiohttp
import requests
from dotenv import load_dotenv
from langchain.schema import BaseOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from exa_py import Exa
from coinmarketcapapi import CoinMarketCapAPI
import pandas as pd
import json

from prompts import portfolio_holdings_prompt
from utils import update_request_status, save_graph_visualization

logger = logging.getLogger(__name__)

load_dotenv('.env', override=True)

# loading env variables
api_key = os.getenv("LLM_API_KEY")
model_name = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")
temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
base_url = os.getenv("LLM_BASE_URL")
EXA_API_KEY = os.getenv("EXA_API_KEY")

# CoinMarketCap API setup
CMC_API_KEY = "7863b798-c214-4e1d-9009-bc303a583c6f"
cmc = CoinMarketCapAPI(CMC_API_KEY)

def fetch_latest_crypto_listings(limit: int = 1000) -> pd.DataFrame:
    response = cmc.cryptocurrency_listings_latest(limit=limit)
    return pd.DataFrame(response.data)

def get_quotes_from_symbols(df: pd.DataFrame, symbols: list = []) -> str:
    filtered = df[df['symbol'].isin([sym.upper() for sym in symbols])]
    if filtered.empty:
        return ""
    result = filtered[['name', 'symbol', 'quote']].copy()
    def extract_usd_quote(row):
        q = row['quote']['USD']
        return pd.Series({
            'Price (USD)': q['price'],
            'Market Cap': q['market_cap'],
            'Market Cap Dominance': q.get('market_cap_dominance'),
            '24h % Change': q['percent_change_24h'],
            '7d % Change': q['percent_change_7d'],
            '30d % Change': q.get('percent_change_30d'),
            '60d % Change': q.get('percent_change_60d'),
            '90d % Change': q.get('percent_change_90d'),
            'Last Updated': q['last_updated'],
        })
    result = result.join(result.apply(extract_usd_quote, axis=1))
    result.drop(columns=['quote'], inplace=True)
    formatted = []
    for _, row in result.iterrows():
        line = (
            f"{row['name']} ({row['symbol']}):\n"
            f"  Price: ${row['Price (USD)']:.2f}\n"
            f"  Market Cap: ${row['Market Cap']:,.0f}\n"
            f"  Market Cap Dominance: {row['Market Cap Dominance']:.2f}%\n"
            f"  24h % Change: {row['24h % Change']:.2f}%\n"
            f"  7d % Change: {row['7d % Change']:.2f}%\n"
            f"  30d % Change: {row['30d % Change']:.2f}%\n"
            f"  60d % Change: {row['60d % Change']:.2f}%\n"
            f"  90d % Change: {row['90d % Change']:.2f}%\n"
            f"  Last Updated: {row['Last Updated']}\n"
        )
        formatted.append(line)
    return "\n".join(formatted)

class FinanceNewsFetcher:
    def __init__(self, api_key: str):
        self.exa = Exa(api_key)

    def fetch_news(self, keywords: List[str], num_results: int = 20, time_range: str = "last 24 hours") -> List[Dict]:
        keyword_query = " OR ".join(keywords)
        query = f"({keyword_query}) AND published within the {time_range}"
        
        results = self.exa.search_and_contents(
            query=query,
            num_results=num_results,
            use_autoprompt=True,
            text=True,
            highlights=True
        )

        articles = []
        for result in results.results:
            articles.append({
                "title": result.title,
                "url": result.url,
                "published_date": result.published_date,
                "highlights": result.highlights,
                "sentiment": "neutral",  # Default sentiment
                "relevance_score": 0.5,  # Default relevance score
                "impact": "medium"  # Default impact
            })
        return articles

def format_news(news_items: list) -> str:
    formatted = ""
    for i, item in enumerate(news_items, 1):
        title = item["title"]
        highlights = item.get("highlights", [])
        highlight_text = " ".join(highlights).strip()
        formatted += f"{i}. {title}\n{highlight_text}\n\n"
    return formatted.strip()

# This is a parser that removes the think tag from the output
class AfterThinkTagParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        parts = text.split("</think>")
        if len(parts) > 1:
            return parts[1].strip()
        return text.strip()

class AgentState(TypedDict):
    question: str
    portfolio_holdings: Optional[Dict[str, float]]
    current_prices: Optional[Dict[str, float]]
    news_data: Optional[List[Dict[str, Any]]]
    coinmarketcap_quotes: Optional[str]
    telegram_messages: Optional[str]
    # analyzed_news: Optional[List[Dict[str, Any]]]
    # filtered_news: Optional[List[Dict[str, Any]]]



llm = ChatOpenAI(model=model_name, temperature=temperature, api_key=api_key, base_url=base_url)

# Create the portfolio holdings chain
portfolio_holdings_chain = (
    {
        "portfolio_holdings": lambda x: x["portfolio_holdings"],
        "coinmarketcap_quotes": lambda x: x["coinmarketcap_quotes"],
        "news_data": lambda x: x["news_data"],
        "telegram_messages": lambda x: x["telegram_messages"]
    }
    | ChatPromptTemplate.from_template(portfolio_holdings_prompt)
    | llm
    | StrOutputParser()
)

def get_portfolio_holdings(state: AgentState) -> AgentState:
    """
    Get the portfolio holdings and generate a description.
    """
    state["portfolio_holdings"] = {"solana": 1, "bitcoin": 2, "ethereum": 1, "polkadot": 1}
    print(state["portfolio_holdings"])
    return state

def get_current_prices(state: AgentState) -> AgentState:
    """
    Get the current prices of the portfolio holdings.
    """
    state["current_prices"] = {"solana": 100, "bitcoin": 200, "ethereum": 100, "polkadot": 100}
    print(state["current_prices"])
    return state


def get_coinmarketcap(state: AgentState) -> AgentState:
    """
    Fetch latest crypto quotes for portfolio holdings and add to state.
    """
    try:
        holdings = state.get("portfolio_holdings", {})
        symbols = list(holdings.keys())
        df = fetch_latest_crypto_listings()
        quotes = get_quotes_from_symbols(df, symbols)
        state["coinmarketcap_quotes"] = quotes
        print("CoinMarketCap quotes:\n", quotes)
    except Exception as e:
        print(f"Error in get_coinmarketcap: {e}")
        state["coinmarketcap_quotes"] = f"Error: {e}"
    return state

# Update news_retrieval to include coinmarketcap_quotes

def news_retrieval(state: AgentState) -> AgentState:
    """
    Retrieve and analyze relevant news for the portfolio.
    """
    try:
        if not EXA_API_KEY:
            raise ValueError("EXA_API_KEY is missing. Please set it in .env file.")
        holdings = state.get("portfolio_holdings", {})
        keywords = []
        for asset in holdings.keys():
            keywords.append(f"{asset} cryptocurrency")
            keywords.append(f"{asset} price")
            keywords.append(f"{asset} news")
        print("the keywords are: ", keywords)
        keywords.extend([
            "cryptocurrency market",
            "crypto trading",
            "blockchain technology",
            "defi news",
            "nft market",
            "web3 development"
        ])
        fetcher = FinanceNewsFetcher(EXA_API_KEY)
        articles = fetcher.fetch_news(
            keywords=keywords,
            num_results=20,
            time_range="last 24 hours"
        )
        state["news_data"] = articles
        print("the news data is: ", state["news_data"])
        # Add coinmarketcap quotes to news node output
        state["coinmarketcap_quotes"] = state.get("coinmarketcap_quotes", "")
    except Exception as e:
        print(f"Error in news retrieval: {e}")
        state["news_data"] = [{"error": str(e)}]
        state["coinmarketcap_quotes"] = state.get("coinmarketcap_quotes", f"Error: {e}")
    return state

# Define the news analysis node function
def analysis_news(state: AgentState) -> AgentState:
    """
    Perform deep analysis on the news articles.
    """
    input_data = {
        "portfolio_holdings": state["portfolio_holdings"],
        "coinmarketcap_quotes": state["coinmarketcap_quotes"],
        "news_data": state["news_data"],
        "telegram_messages": state["telegram_messages"]
    }
    res = portfolio_holdings_chain.invoke(input_data)
    print("\n\n\n\n")
    print("the res is: ", res)
    return state

def get_telegram_messages(state: AgentState) -> AgentState:
    """
    Retrieve messages from relevant Telegram channels.
    """
    try:
        from telegram import TelegramFetcher
        
        channels = [
            "whale_alert",
            "bitexgroupsignal"
        ]
        
        fetcher = TelegramFetcher()
        messages = fetcher.get_messages(channels)
        print("the messages are: ", messages)
        state["telegram_messages"] = messages
        logger.info("Successfully fetched Telegram messages")
    except Exception as e:
        logger.error(f"Error fetching Telegram messages: {e}")
        state["telegram_messages"] = json.dumps({"error": str(e)})
    
    return state

# Create the workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("get_holdings", get_portfolio_holdings)
workflow.add_node("get_prices", get_current_prices)
workflow.add_node("get_coinmarketcap", get_coinmarketcap)
workflow.add_node("get_news", news_retrieval)
workflow.add_node("get_telegram", get_telegram_messages)
workflow.add_node("analysis_news", analysis_news)

# Add edges
workflow.add_edge("get_holdings", "get_prices")
workflow.add_edge("get_prices", "get_coinmarketcap")
workflow.add_edge("get_coinmarketcap", "get_news")
workflow.add_edge("get_news", "get_telegram")
workflow.add_edge("get_telegram", "analysis_news")
workflow.add_edge("analysis_news", END)

# Set the entry point
workflow.set_entry_point("get_holdings")

# Compile the graph
app = workflow.compile()

# Save the graph visualization
save_graph_visualization(app, "portfolio_news_workflow.png")

# Function to invoke the agent
def invoke_agent(question: str) -> Dict[str, Any]:
    """
    Invoke the agent with a question and get the results.
    
    Args:
        question (str): The question or query to analyze
        
    Returns:
        Dict[str, Any]: The complete state after running through all nodes
    """
    # Initialize the state
    initial_state = {
        "question": question
    }
    
    # Run the workflow
    result = app.invoke(initial_state)
    return result

if __name__ == "__main__":
    # Example usage
    question = "Analyze my portfolio holdings base on the market"
    result = invoke_agent(question)
    
    # Print the results
    # print("\n=== Portfolio Holdings ===")
    # print(result.get("portfolio_holdings", {}))
    
    # print("\n=== Current Prices ===")
    # print(result.get("current_prices", {}))

    # print("\n=== CoinMarketCap Quotes ===")
    # print(result.get("coinmarketcap_quotes", {}))

    # print("\n=== News Data ===")
    # print(result.get("news_data", {}))
