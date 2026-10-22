from langchain_exa import ExaSearchRetriever
import os
from dotenv import load_dotenv
# finance_news_fetcher.py
from exa_py import Exa
from typing import List, Dict



exa_key = "a85cb165-68fc-4d5d-af53-4dd5d61b1401"
load_dotenv()
EXA_API_KEY = os.getenv(exa_key)




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
                "highlights": result.highlights
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


def get_finance_news(
    keywords: List[str],
    num_results: int = 20,
    time_range: str = "last 24 hours"
) -> str:
    """
    High-level function to get finance news results both structured and formatted.

    Args:
        keywords (List[str]): Keywords to search.
        num_results (int): Number of news results to fetch.
        time_range (str): Time filter for news (e.g., "last 3 days").

    Returns:
        Dict[str, object]: {
            "articles": List[NewsArticle],
            "formatted": str
        }
    """
    if not EXA_API_KEY:
        raise ValueError("EXA_API_KEY is missing. Please set it in .env file.")

    fetcher = FinanceNewsFetcher(EXA_API_KEY)
    articles = fetcher.fetch_news(keywords, num_results=num_results, time_range=time_range)
    formatted_text = format_news(articles)
    return formatted_text
    