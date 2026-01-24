# app/tasks/jobs.py
import asyncio
from typing import List
import numpy as np
from datetime import datetime

from app.services.data_ingest import save_index_statistics, save_stock_data, save_index_data, save_stock_predictions, save_stock_rank, save_stock_statistics
from app.repositories.indexes import get_any_date_index_price, get_last_index_days200_end_date, get_several_index_statistics, select_index_start_date, get_last_date_index_price, get_several_index_price, get_last_index_window_end_date
from app.repositories.stocks import get_any_date_stock_price, get_industry_stock_category, get_last_date_stock_price, get_last_stock_days200_end_date, get_last_stock_window_end_date, get_sector_stock_category, get_several_stock_price, get_several_stock_statistics, select_stock_start_date
from app.tasks.algorithm import calculate_stock_potensoial, days_index_moving_average, days_stock_moving_average
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

# Run index statistics calculation on server startup
def run_index_statistics_on_startup(ticker: str = "^GSPC"):
    try:
        last_index_date = get_last_date_index_price()
        last_days200_end_date = get_last_index_days200_end_date()

        """
        # Skip prediction if no new data since last prediction
        if last_index_date == last_days200_end_date:
            print(f"⭕️ Skipping index statistics, no new data since last statistics on {last_days200_end_date}.")
            return
        """
        

        # Data post-processing
        days200_start_date = get_any_date_index_price(ticker, 200)
        days200_end_date = get_last_date_index_price()
        days200_ma = days_index_moving_average(ticker, 200)

        # Prepare data for insertion
        data = {}
        data['ticker'] = ticker
        data['days200_start_date'] = days200_start_date
        data['days200_end_date'] = days200_end_date
        data['days200_ma'] = days200_ma

        # Insert data into index_statistics table
        save_index_statistics(data, ticker)
    except Exception as e:
        print(f"❌ Error during startup index {ticker} statistics: {e}")

# Run stock statistics calculation on server startup
def run_stock_statistics_on_startup(tickers: List[str]):
    try:
        for ticker in tickers:
            last_stock_date = get_last_date_stock_price()
            last_days200_end_date = get_last_stock_days200_end_date()
            
            """
            # Skip prediction if no new data since last prediction
            if last_stock_date == last_days200_end_date:
                print(f"⭕️ Skipping stock statistics, no new data since last statistics on {last_days200_end_date}.")
                continue
            """
            

            # Data post-processing
            days200_start_date = get_any_date_stock_price(ticker, 200)
            days200_end_date = get_last_date_stock_price()
            days200_ma = days_stock_moving_average(ticker, 200)
            # Prepare data for insertion
            data = {}
            data['ticker'] = ticker
            data['days200_start_date'] = days200_start_date
            data['days200_end_date'] = days200_end_date
            data['days200_ma'] = days200_ma
            # Insert data into index_statistics table
            save_stock_statistics(data, ticker)
    except Exception as e:
        print(f"❌ Error during startup stock statistics: {e}")

# Run index prediction on server startup
def run_index_prediction_on_startup(ticker: str = "^GSPC"):
    try:
        last_index_date = get_last_date_index_price()
        last_window_end_date = get_last_index_window_end_date()
        window_size = get_model_params("timesteps")
        last_days200_ma = get_several_index_statistics(symbols=[ticker], columns=['days200_ma'], limit=1)

        # Skip prediction if no new data since last prediction
        """if last_index_date == last_window_end_date:
            print(f"⭕️ Skipping index prediction, no new data since last prediction on {last_window_end_date}.")
            return"""

        # Get latest days(window size) of close and volume for ticker
        df = get_several_index_price([ticker], ['close', 'volume'], limit=window_size)

        # Check data sufficiency
        if df.empty or len(df) < int(window_size):
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
        
        # Data post-processing
        window_start_date = get_any_date_index_price(ticker, window_size)
        window_end_date = last_index_date
        predicted_scaled = np.array(result['prediction']).reshape(-1, 1)
        predicted_real = destandardize_data(predicted_scaled) # Destandardize predicted value
        last_actual_close = closes[-1, 0]
        recommendation = "BUY" if predicted_real >= last_days200_ma['days200_ma'][0] else "SELL"
        feature_number = get_model_params("num_features")
        input_features_length = len(result['input_features'])
        
        # Prepare data for insertion
        data = {}
        data['ticker'] = ticker
        data['window_size'] = window_size
        data['window_start_date'] = window_start_date
        data['window_end_date'] = window_end_date
        data['predicted_scaled'] = predicted_scaled[0, 0]
        data['predicted_real'] = predicted_real
        data['last_actual_close'] = last_actual_close
        data['recommendation'] = recommendation
        data['feature_number'] = feature_number
        data['input_features_length'] = input_features_length

        # Insert data into index_predictions table
        save_index_predictions(data, ticker)
        
        print(f"📈 Index {ticker} Prediction result on startup:")
        print(f"Predicted scaled: {predicted_scaled[0, 0]}")
        print(f"Predicted real close price: {predicted_real}")
        print(f"Last actual close: {last_actual_close}")
        print(f"Recommendation: {recommendation}")
    except Exception as e:
        print(f"❌ Error during startup index prediction: {e}")

# Run stock prediction on server startup
def run_stock_prediction_on_startup(tickers: List[str]):
    try:
        for ticker in tickers:
            last_stock_date = get_last_date_stock_price()
            last_window_end_date = get_last_stock_window_end_date()
            window_size = get_model_params("timesteps")
            last_days200_ma = get_several_stock_statistics(symbols=[ticker], columns=['days200_ma'], limit=1)

            """# Skip prediction if no new data since last prediction
            if last_stock_date == last_window_end_date:
                print(f"⭕️ Skipping stock prediction, no new data since last prediction on {last_window_end_date}.")
                return"""

            # Get latest days(window size) of close and volume for ticker
            df = get_several_stock_price([ticker], ['close', 'volume'], limit=window_size)

            
            # Check data sufficiency
            if df.empty or len(df) < int(window_size):
                print(f"⚠️ Not enough stock data {ticker} for prediction (need {window_size} days)")
                continue
            
            
            
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
            window_start_date = get_any_date_stock_price(ticker, window_size)
            window_end_date = last_stock_date
            predicted_scaled = np.array(result['prediction']).reshape(-1, 1)
            predicted_real = destandardize_data(predicted_scaled) # Destandardize predicted value
            last_actual_close = closes[-1, 0]
            recommendation = "BUY" if predicted_real >= last_days200_ma['days200_ma'][0] else "SELL"
            feature_number = get_model_params("num_features")
            input_features_length = len(result['input_features'])
            
            # Prepare data for insertion
            data = {}
            data['ticker'] = ticker
            data['window_size'] = window_size
            data['window_start_date'] = window_start_date
            data['window_end_date'] = window_end_date
            data['predicted_scaled'] = predicted_scaled[0, 0]
            data['predicted_real'] = predicted_real
            data['last_actual_close'] = last_actual_close
            data['recommendation'] = recommendation
            data['feature_number'] = feature_number
            data['input_features_length'] = input_features_length

            # Insert data into stock_predictions table
            save_stock_predictions(data, ticker)
            
            print(f"📈 stock {ticker} Prediction result on startup:")
            print(f"Predicted scaled: {predicted_scaled[0, 0]}")
            print(f"Predicted real close price: {predicted_real}")
            print(f"Last actual close: {last_actual_close}")
            print(f"Recommendation: {recommendation}")
    except Exception as e:
        print(f"❌ Error during startup stock prediction: {e}")


def run_stock_rank_on_startup(tickers: List[str]):
    try:
        temp_po = {}
        #temp_po['ticker'] = [{}]
        #temp_po['ticker']['potential'] = ""

        temp_rn = {}
        #temp_rn['ticker']['rank_number'] = ""
        for ticker in tickers:
            potential = calculate_stock_potensoial(ticker)
            print(f"potential: {potential}")
            if potential is not None:
                temp_po[ticker] = potential
            else:
                continue

        sorted_temp_po = {k: v for k, v in sorted(temp_po.items(), key=lambda item: item[1], reverse=True)}
        print(f"sorted_temp_po: {sorted_temp_po}")
            
        """for ticker in tickers:
            # Data post-processing
            sector = get_sector_stock_category(ticker)
            industry = get_industry_stock_category(ticker)
            current_price = get_several_stock_price([ticker], ['close'], limit=1)['close'][0]
            potential = temp['potential']

            # Prepare data for insertion
            data = {}
            data['ticker'] = ticker
            data['sector'] = sector
            data['industry'] = industry
            data['current_price'] = current_price
            data['potential'] = potential

            # Insert data into stock_rank table
            save_stock_rank(data, ticker)

            print(f"📈 stock {ticker} Potential result on startup:")
            print(f"Potential: {potential}%")"""

        """ # backup
        for ticker in tickers:
            # Data post-processing
            sector = get_sector_stock_category(ticker)
            industry = get_industry_stock_category(ticker)
            current_price = get_several_stock_price([ticker], ['close'], limit=1)['close'][0]
            potential = calculate_stock_potensoial(ticker)

            # Prepare data for insertion
            data = {}
            data['ticker'] = ticker
            data['sector'] = sector
            data['industry'] = industry
            data['current_price'] = current_price
            data['potential'] = potential

            # Insert data into stock_rank table
            save_stock_rank(data, ticker)

            print(f"📈 stock {ticker} Potential result on startup:")
            print(f"Potential: {potential}%")"""
    except Exception as e:
        print(f"❌ Error during startup stock ranking: {e}")
