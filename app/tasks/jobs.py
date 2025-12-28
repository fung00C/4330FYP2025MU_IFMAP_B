# app/tasks/jobs.py
import asyncio
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler

from app.services.data_ingest import save_stock_data, save_index_data
from app.repositories.indexes import get_last_index_date, get_several_index_price
from app.repositories.stocks import get_last_stock_date
from app.utils.app_state import get_tickers
from app.tasks.predictions import predict, PredictionInput

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

def run_prediction_on_startup():
    try:
        # Get latest 60 days of close and volume for ^GSPC
        df = get_several_index_price(['^GSPC'], ['close', 'volume'], limit=60)
        if df.empty or len(df) < 60:
            print("⚠️ Not enough index data for prediction (need 60 days)")
            return

        #  Create an instance of the StandardScalers for input features and output
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()

        # Prepare X, y
        closes = df['close'].values.astype(float).reshape(-1, 1)
        volumes = df['volume'].values.astype(float).reshape(-1, 1)
        X = np.hstack([closes, volumes]) # shape (60, 2) ; hstack to horizontally stack arrays
        y = closes # shape (60, 1)

        # Standardize using StandardScaler
        X_scaled = scaler_X.fit_transform(X)
        y_scaled = scaler_y.fit_transform(y)

        # Prepare features: [close1_scaled, volume1_scaled, close2_scaled, volume2_scaled, ..., close60_scaled, volume60_scaled]
        features = X_scaled.reshape(-1).tolist()

        # Check if enough data
        if len(features) != 120:
            print(f"⚠️ Features length {len(features)} != 120, skipping prediction")
            return

        # Create PredictionInput
        input_data = PredictionInput(features=features)

        # Run prediction
        result = predict(input_data)
        predicted_scaled = np.array(result['prediction']).reshape(-1, 1)

        # The prediction is for the next close price, scaled. Inverse transform to get real value
        predicted_real = scaler_y.inverse_transform(predicted_scaled)[0, 0]
        last_actual_close = closes[-1, 0]

        print("📈 Prediction result on startup:")
        print(f"Predicted scaled: {predicted_scaled[0, 0]}")
        print(f"Predicted real close price: {predicted_real}")
        print(f"Last actual close: {last_actual_close}")
        print(f"Input features length: {len(result['input_features'])}")
    except Exception as e:
        print(f"❌ Error during startup prediction: {e}")
