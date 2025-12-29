# app/tasks/jobs.py
import asyncio
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler

from app.services.data_ingest import save_stock_data, save_index_data
from app.repositories.indexes import get_last_index_date, get_several_index_price
from app.repositories.stocks import get_last_stock_date
from app.utils.app_state import get_tickers
from app.tasks.predictions import destandardize_data, predict, standardize_data, PredictionInput
from app.services.data_ingest import save_index_prediction

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
        return

def run_index_prediction_on_startup(ticker: str = "^GSPC"):
    try:
        # Get latest 60 days of close and volume for ticker
        df = get_several_index_price([ticker], ['close', 'volume'], limit=60)

        # Check data sufficiency
        if df.empty or len(df) < 60:
            print(f"⚠️ Not enough index data {ticker} for prediction (need 60 days)")
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

        # Data post-processing
        predicted_scaled = np.array(result['prediction']).reshape(-1, 1)
        predicted_real = destandardize_data(predicted_scaled) # Destandardize predicted value
        last_actual_close = closes[-1, 0]
        input_features_length = len(result['input_features'])
        data = {}
        data['predicted_scaled'] = predicted_scaled[0, 0]
        data['predicted_real'] = predicted_real
        data['last_actual_close'] = last_actual_close
        data['input_features_length'] = input_features_length

        print(f"📈 Index {ticker} Prediction result on startup:")
        print(f"Predicted scaled: {predicted_scaled[0, 0]}")
        print(f"Predicted real close price: {predicted_real}")
        print(f"Last actual close: {last_actual_close}")
        print(f"Input features length: {input_features_length}")

        # Insert data into index_predictions table
        save_index_prediction(data, ticker)
    except Exception as e:
        print(f"❌ Error during startup index {ticker} prediction: {e}")
