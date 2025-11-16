# app/utils/pandas_helper.py
import pandas as pd
import sqlite3

def append_df(ticker, df: pd.DataFrame, table: str, conn: sqlite3.Connection, chunksize: int = 1000) -> None:
    # validate data
    if df.empty or df['close'].sum() == 0:
        raise ValueError(f"No valid data after processing for {ticker}")
    df.to_sql(table, conn, if_exists="append", index=False, method="multi", chunksize=chunksize) # append to stock_price table, no index, multi insert, chunk size 1000 for large data
    conn.commit()
