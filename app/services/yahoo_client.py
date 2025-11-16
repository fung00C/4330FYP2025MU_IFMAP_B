# app/services/yahoo_client.py
import yfinance as yf
from datetime import datetime
from typing import List, Optional
import pandas as pd

# download index data for a ticker from Yahoo Finance and store it in the database financial.db
def download_index(ticker: str = "^GSPC", start_date: str = "2015-01-01", end_date: Optional[str] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    # download a ticker data
    print(f"📥 Downloading index data for {len(ticker)} tickers from {start_date} to {end_date}")
    data = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False, auto_adjust=True)
    # ensure data is not empty
    if data is None or data.empty:
        raise ValueError(f"No data found for the given 'ticker' {ticker}.")
    return data

# download stock data for a list of tickers from Yahoo Finance and store it in the database financial.db
def download_stocks(tickers: List[str], start_date: str = "2015-01-01", end_date: Optional[str] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    # download all tickers data at once with built-in multithreading
    print(f"📥 Downloading stock data for {len(tickers)} tickers from {start_date} to {end_date}")
    all_data = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        group_by='ticker',
        threads=True,
        progress=False,
        auto_adjust=True
    )  # auto adjust Close price to avoid Adj Close issues
    # ensure data is not empty
    if all_data is None or all_data.empty:
        raise ValueError("No data found for the given list 'tickers'.")
    return all_data
