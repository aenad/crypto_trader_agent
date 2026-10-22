import os
import pandas as pd
from coinmarketcapapi import CoinMarketCapAPI
from typing import List

API_KEY = "7863b798-c214-4e1d-9009-bc303a583c6f"
cmc = CoinMarketCapAPI(API_KEY)

def fetch_latest_crypto_listings(limit: int = 1000) -> pd.DataFrame:
    """
    Args:
        limit (int): Max number of listings.
    Returns:
        pd.DataFrame: Full listings data.
    """
    response = cmc.cryptocurrency_listings_latest(limit=limit)
    return pd.DataFrame(response.data)

def get_quotes_from_symbols(df: pd.DataFrame, symbols: List[str] = []) -> pd.DataFrame:
    """
    Args:
        df (pd.DataFrame): Listings DataFrame.
        symbols (List[str]): Coin symbols to filter.
    Returns:
        pd.DataFrame: Quotes for matched symbols.
    """
    filtered = df[df['symbol'].isin([sym.upper() for sym in symbols])]
    if filtered.empty:
        return pd.DataFrame()

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
    # Format the DataFrame into a string
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

def fetch_and_print_quotes(symbols: List[str]) -> str:
    """
    Fetch and print quotes for the specified cryptocurrency symbols.

    Args:
        symbols (List[str]): List of crypto symbols to fetch quotes for.

    Returns:
        str: Formatted string containing quote information.
    """
    full_df = fetch_latest_crypto_listings()
    quotes = get_quotes_from_symbols(full_df, symbols)
    return quotes

if __name__ == "__main__":
    symbols_to_check = ["BTC", "ETH", "SOL"]
    print(fetch_and_print_quotes(symbols_to_check))