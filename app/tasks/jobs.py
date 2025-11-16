# app/tasks/jobs.py
import asyncio
from datetime import datetime
from app.services.data_ingest import save_stock_data, save_index_data
from app.repositories.indexes import get_last_index_date
from app.repositories.stocks import get_last_stock_date
from app.utils.app_state import get_tickers

# update stock data job for scheduler of daily updates
async def update_financial_data_job(arg:str = "schedule"):
    # set start_date to next day
    index_start_date = get_last_index_date()
    stock_start_date = get_last_stock_date()
    # set end_date to today
    end_date = datetime.now().strftime("%Y-%m-%d")
    match arg:
        case "schedule":
            print(f"Scheduled job: Updating financial data from {stock_start_date} to {end_date}")
        case "manual":
            print(f"Manually by URL: Updating financial data from {index_start_date} to {end_date}")
    if get_tickers():
        if index_start_date != end_date:
            await asyncio.to_thread(save_index_data, start_date=index_start_date, end_date=end_date)
        else:
            print("⭕️ The index data is up to date in the financial database")
        if stock_start_date != end_date:
            await asyncio.to_thread(save_stock_data, get_tickers(), start_date=stock_start_date, end_date=end_date) # download and save in a thread to avoid blocking the event loop
        else:
            print("⭕️ The stock data is up to date in the financial database")
    else:
        print("⚠️ No tickers found for scheduled update")
