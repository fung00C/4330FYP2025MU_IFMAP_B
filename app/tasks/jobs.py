# app/tasks/jobs.py
import asyncio
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler

from app.services.data_ingest import save_stock_data, save_index_data
from app.repositories.indexes import get_any_index_date, select_index_start_date, get_last_index_date, get_several_index_price, get_last_index_window_end_date
from app.repositories.stocks import select_stock_start_date, get_last_stock_date
from app.tasks.technical_indicator import days_moving_average
from app.utils.app_state import get_tickers, get_model_params
from app.tasks.predictions import destandardize_data, predict, standardize_data, PredictionInput
from app.services.data_ingest import save_index_predictions

# update stock data job for scheduler of daily updates
async def update_financial_data_job(arg:str = "schedule"):
    # set start_date to next day
    index_start_date = select_index_start_date()
    stock_start_date = select_stock_start_date()
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
        return

def run_index_prediction_on_startup(ticker: str = "^GSPC"):
    try:
        last_index_date = get_last_index_date()
        last_window_end_date = get_last_index_window_end_date()
        window_size = get_model_params("timesteps")

        # Skip prediction if no new data since last prediction
        if last_index_date == last_window_end_date:
            print(f"⭕️ Skipping index prediction, no new data since last prediction on {last_window_end_date}.")
            return

        # Get latest days(window size) of close and volume for ticker
        df = get_several_index_price([ticker], ['close', 'volume'], limit=window_size)

        # Check data sufficiency
        if df.empty or len(df) < window_size:
            print(f"⚠️ Not enough index data {ticker} for prediction (need {window_size} days)")
            return
        
        # Prepare standardized features
        closes = df['close'].values.astype(float).reshape(-1, 1)
        volumes = df['volume'].values.astype(float).reshape(-1, 1)

        # Standardize data
        features = standardize_data(closes, volumes)

        # Create PredictionInput
        input_data = PredictionInput(features=features)

        # Run prediction
        result = predict(input_data)
        print(f"📈 Index {ticker} Prediction result on startup:")
        print(f"Predicted scaled: {predicted_scaled[0, 0]}")
        print(f"Predicted real close price: {predicted_real}")
        print(f"Last actual close: {last_actual_close}")

        # Data post-processing
        window_start_date = get_any_index_date(ticker, window_size)
        window_end_date = last_index_date
        predicted_scaled = np.array(result['prediction']).reshape(-1, 1)
        predicted_real = destandardize_data(predicted_scaled) # Destandardize predicted value
        last_actual_close = closes[-1, 0]
        feature_number = get_model_params("num_features")
        input_features_length = len(result['input_features'])
        
        # Prepare data for insertion
        data_pd = {}
        data_pd['ticker'] = ticker
        data_pd['window_size'] = window_size
        data_pd['window_start_date'] = window_start_date
        data_pd['window_end_date'] = window_end_date
        data_pd['predicted_scaled'] = predicted_scaled[0, 0]
        data_pd['predicted_real'] = predicted_real
        data_pd['last_actual_close'] = last_actual_close
        data_pd['feature_number'] = feature_number
        data_pd['input_features_length'] = input_features_length

        # Insert data into index_predictions table
        save_index_predictions(data_pd, ticker)

        # Data post-processing
        days200_start_date = get_any_index_date(ticker, 200)
        days200_end_date = get_last_index_date()
        days200_ma = days_moving_average(ticker, 200)

        # Prepare data for insertion
        data_st = {}
        data_st['ticker'] = ticker
        data_st['days200_start_date'] = days200_start_date
        data_st['days200_end_date'] = days200_end_date
        data_st['days200_ma'] = days200_ma

        # Insert data into index_statistics table
        save_index_statistics(data_st, ticker)
    except Exception as e:
        print(f"❌ Error during startup index {ticker} prediction: {e}")
