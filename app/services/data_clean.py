# app/services/data_clean.py
from typing import List, Dict
import pandas as pd

def clean_index_df(data:pd.DataFrame, ticker: str) -> pd.DataFrame:
    # process and store data
    df = data.reset_index()  # extract ticker DataFrame and reset index
    df.columns = ["date", "open", "high", "low", "close", "volume"]  # rename columns
    df["symbol"] = ticker  # add symbol column
    df = df[["symbol", "date", "open", "high", "low", "close", "volume"]]

    # Data cleaning and type conversion
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    numeric_columns = ["open", "high", "low", "close"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(0.0).astype(float)
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype(int)
    return df

def clean_stock_panel(all_data:pd.DataFrame, tickers: List[str]) -> Dict[str, pd.DataFrame]:
    # process and store data for each ticker
    cleaned = {}
    for ticker in tickers:
        if ticker not in all_data.columns.levels[0]:  # check if ticker data exists in downloaded data
            raise KeyError(f"Ticker {ticker} not in downloaded data (possibly delisted)")
        df = all_data[ticker].reset_index()  # extract ticker DataFrame and reset index
        df = df.rename(columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })  # rename columns
        df["symbol"] = ticker  # add symbol column
        df = df[["symbol", "date", "open", "high", "low", "close", "volume"]]  # reorder columns, select relevant columns only
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")  # format date as string YYYY-MM-DD, remove time part
        numeric_columns = ["open", "high", "low", "close"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].fillna(0.0).astype(float)
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype(int)
        cleaned[ticker] = df
    return cleaned
