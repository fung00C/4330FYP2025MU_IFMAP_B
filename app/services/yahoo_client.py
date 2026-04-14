# app/services/yahoo_client.py
import yfinance as yf
from datetime import datetime
from typing import List, Optional
import pandas as pd

from app.services.data_refresh import refresh_tickers_list
from app.utils.app_state import set_failed_tickers

# download index data for a ticker from Yahoo Finance and store it in the database financial.db
def download_index(ticker: str = "^GSPC", start_date: str = "2015-01-01", end_date: Optional[str] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    # download a ticker data
    print(f"📥 Downloading index data from {start_date} to {end_date}")
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
    # check for failed tickers, save, and log them
    failed_tickers_dict = yf.shared._ERRORS
    failed_tickers_list = list(failed_tickers_dict.keys())
    set_failed_tickers(failed_tickers_list)
    if failed_tickers_list:
        print(f"⚠️ Failed tickers: {failed_tickers_list}. Check if they are delisted or invalid.")
    # refresh tickers list by removing failed tickers
    refresh_tickers_list(failed_tickers_list)
    return all_data

