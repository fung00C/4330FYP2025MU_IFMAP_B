# app/services/data_ingest.py
import json
import os
import pandas as pd
import logging
import sqlite3
from typing import List
from datetime import datetime, timedelta

from app.repositories.stocks import get_stock_category
from app.services.yahoo_client import download_index, download_stocks
from app.services.data_clean import clean_index_df, clean_stock_panel
from app.services.data_refresh import refresh_tickers_list
from app.utils.file import open_sql_file
from app.utils.pandas_helper import append_df
from app.utils.app_state import get_fin_db, get_sql_path, set_tickers
from app.repositories.meta import get_ticker_symbols

logger = logging.getLogger(__name__)

# Save index data into financial.db
def save_index_data(ticker: str = "^GSPC", start_date: str = "2015-01-01", end_date: str = "2025-10-01"): # None
    failed_tickers = []  # track failed tickers
    try:
        data = download_index(ticker=ticker, start_date=start_date, end_date=end_date)
        df = clean_index_df(data, ticker)
        try:
            append_df(ticker, df, table="index_price", conn=get_fin_db())
            print(f"✅ Data for {ticker} fetched and stored successfully | Saved {len(df)} rows for {ticker}")
        except Exception as ticker_error:
            print(f"⭕️ Skipping {ticker} due to error: {ticker_error}")
        if failed_tickers:
            print(f"⚠️ Failed tickers: {failed_tickers}. Check if they are delisted or invalid.")
        return {"success": True, "failed tickers": failed_tickers}
    except Exception as e:
        print(f"❌ An error occurred during download: {e}")
        return {"success": False, "error": str(e)}

# Save stock data into financial.db
def save_stock_data(tickers: List[str], start_date: str = "2015-01-01", end_date: str = "2025-10-01"): # None
    failed_tickers = []  # track failed tickers
    try:
        all_data = download_stocks(tickers=tickers, start_date=start_date, end_date=end_date)
        cleaned = clean_stock_panel(all_data, tickers)
        for ticker, df in cleaned.items(): 
            try:
                append_df(ticker, df, table="stock_price", conn=get_fin_db())
                print(f"✅ Data for {ticker} fetched and stored successfully | Saved {len(df)} rows for {ticker}")
            except Exception as ticker_error:
                failed_tickers.append(ticker)
                print(f"⭕️ Skipping {ticker} due to error: {ticker_error}")
        if failed_tickers:
            print(f"⚠️ Failed tickers: {failed_tickers}. Check if they are delisted or invalid.")
            #refresh_tickers_list(failed_tickers) #TODO
        return {"success": True, "failed tickers": failed_tickers}
    except Exception as e:
        print(f"❌ An error occurred during download: {e}")
        return {"success": False, "error": str(e)}

# Save stock detail from CSV to financial.db
def save_stock_detail(database: str = "financial.db"):
    try:
        df = pd.read_csv('sp500_companies.csv')  # Load CSV file
        table_name = 'stock_detail'
        df.to_sql(table_name, get_fin_db() , if_exists='replace', index=False)  # delete table if exists, create table, write DataFrame to SQL table, index=False : avoid to write DataFrame index
        get_fin_db().commit()
        print(f"✅ CSV data successfully saved to table '{table_name}' in {database}.")
        return True
    except Exception as e:
        print(f"❌ An error occurred while saving CSV to database: {e}")
        return False

# store tickers in app.state and in our utils cache for global access
def store_ticker_symbols(app):
    tickers = get_ticker_symbols()
    try:
        if hasattr(app, "state"):
            app.state.tickers = list(tickers) if tickers is not None else [] # store a shallow copy to avoid external mutation
        else:
            raise AttributeError("app has no 'state' attribute") # explicitly raise so we handle it below and log appropriately
    except AttributeError as e:
        logger.debug("app.state not available; tickers stored in utils cache only: %s", e) # expected in some test or minimal contexts; keep a debug log
    except Exception as e:
        logger.exception("Unexpected error while setting app.state.tickers: %s", e) # unexpected errors should be visible in logs for troubleshooting
    set_tickers(tickers) # always set into utils cache as the canonical source for non-request code

# Save index predictions into financial.db
def save_index_prediction(data: List[any], ticker: str):
    try:
        db = get_fin_db()
        cursor = db.cursor()
        sql_template = open_sql_file(get_sql_path("insert_index_predictions_data"))
        prediction_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S") # Prediction is for the next day's close, so timestamp should be tomorrow's date
        cursor.execute(sql_template, (prediction_date, data["predicted_scaled"], data["predicted_real"], data["last_actual_close"], data["input_features_length"]))
        db.commit()
        print(f"✅ Index {ticker} prediction saved successfully.")
        return True
    except sqlite3.Error as e:
        print(f"❌ An error occurred while saving index {ticker} prediction: {e}")
        return False
    
def save_stock_category_json():
    try:
        # Fetch stock category data
        df = get_stock_category()
        # Group by sector and industry, collect symbols
        categories = {}
        for _, row in df.iterrows():
            sector = row['Sector']
            industry = row['Industry']
            symbol = row['Symbol']
            if sector not in categories:
                categories[sector] = {}
            if industry not in categories[sector]:
                categories[sector][industry] = []
            categories[sector][industry].append(symbol)
        # Calculate counts
        num_sectors = len(categories)
        num_industries = sum(len(industries) for industries in categories.values())
        # Convert to new format: {"info": {"num_sectors": ..., "num_industries": ...}, "data": [{sector: {industry: [symbols]}}, ...]}
        result = {
            "info": {
                "num_sectors": num_sectors,
                "num_industries": num_industries
            },
            "data": [{sector: industries} for sector, industries in categories.items()]
        }
        # Save to JSON file
        json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'json', 'stock_category.json')
        with open(json_path, 'w') as json_file:
            json.dump(result, json_file, indent=2)
        print("✅ Stock category JSON file saved successfully.")
        return True
    except Exception as e:
        print(f"❌ An error occurred while saving stock category JSON: {e}")
        return False