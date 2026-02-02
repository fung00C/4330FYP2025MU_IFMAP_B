# app/core/lifespan.py
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.scheduler import scheduler
from app.db.connection import create_connection
from app.utils.app_state import get_user_db, set_fin_db, set_user_db, get_fin_db, get_tickers, get_sql_path
from app.utils.file import open_sql_file
from app.tasks.jobs import run_index_statistics_on_startup, run_stock_prediction_on_startup, run_stock_rank_on_startup, run_stock_statistics_on_startup, update_financial_data_job, run_index_prediction_on_startup
from app.tasks.model import load_model
from app.services.data_ingest import save_stock_category_json, save_stock_detail, save_stock_data, save_index_data, store_ticker_symbols
from app.repositories.meta import create_table

# Initialize data on startup, fetch stock details and data
async def init_data_async(app: FastAPI):
    await asyncio.to_thread(save_stock_detail) # to_thread can avoid blocking the event loop
    await asyncio.to_thread(save_stock_category_json)
    await asyncio.to_thread(create_table, get_fin_db(), "index_price", open_sql_file(get_sql_path("create_stock_price_table")))
    await asyncio.to_thread(create_table, get_fin_db(), "stock_price", open_sql_file(get_sql_path("create_index_price_table")))
    await asyncio.to_thread(create_table, get_fin_db(), "index_statistics", open_sql_file(get_sql_path("create_index_statistics_table")))
    await asyncio.to_thread(create_table, get_fin_db(), "stock_statistics", open_sql_file(get_sql_path("create_stock_statistics_table")))
    await asyncio.to_thread(create_table, get_fin_db(), "index_predictions", open_sql_file(get_sql_path("create_index_predictions_table")))
    await asyncio.to_thread(create_table, get_fin_db(), "stock_predictions", open_sql_file(get_sql_path("create_stock_predictions_table")))
    await asyncio.to_thread(create_table, get_fin_db(), "stock_rank", open_sql_file(get_sql_path("create_stock_rank_table")))
    await asyncio.to_thread(create_table, get_user_db(), "user", open_sql_file(get_sql_path("create_user_table")))
    await asyncio.to_thread(create_table, get_user_db(), "bookmark", open_sql_file(get_sql_path("create_bookmark_table")))
    #await asyncio.to_thread(store_ticker_symbols, app) 
    #await asyncio.to_thread(save_stock_data, get_tickers())
    #await asyncio.to_thread(save_index_data)
    #await asyncio.to_thread(run_index_statistics_on_startup)
    #await asyncio.to_thread(run_stock_statistics_on_startup, get_tickers())
    #await asyncio.to_thread(run_index_prediction_on_startup)
    #await asyncio.to_thread(run_stock_prediction_on_startup, get_tickers()) # TODO: all tickers ['AAPL', 'MSFT', 'GOOGL']
    await asyncio.to_thread(run_stock_rank_on_startup, get_tickers()) # TODO: all tickers ['AAPL', 'MSFT', 'GOOGL']
    
    
    
# Lifespan context manager for FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # server startup event:

    # build global DB connection and attach to app.state
    app.state.fin_db = create_connection("financial.db")  # financial data
    app.state.user_db = create_connection("user.db")  # user data
    # Synchronize to utils.app_state for other modules to access.
    set_fin_db(app.state.fin_db)
    set_user_db(app.state.user_db)
    if app.state.fin_db and app.state.user_db:
        print("✅ Both database connections established.")
    else:
        print("⚠️ Warning: One or both DB connections failed.")

    # load ML model and set parameters
    #load_model()

    # initalize data run in background
    asyncio.create_task(init_data_async(app))

    # schedule daily stock data update job at midnight using a cron trigger to run once a day at 00:00.
    #scheduler.add_job(update_financial_data_job, 'cron', hour=0, minute=0)
    #scheduler.start()

    try:
        yield  # ---> during server runtime
    finally:
        # server shutdown event:
        # close global DB connection
        if getattr(app.state, "fin_db", None):
            app.state.fin_db.close()
            print("financial.db connection closed.")
        if getattr(app.state, "user_db", None):
            app.state.user_db.close()
            print("user_db connection closed.")
        # shutdown scheduler
        scheduler.shutdown()