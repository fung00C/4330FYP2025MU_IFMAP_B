# app/tasks/jobs.py
import asyncio
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http.client import HTTPException
import smtplib
from email.mime.text import MIMEText
from fastapi import HTTPException
from typing import List
import numpy as np
from datetime import datetime, timedelta
from app.routers import email

from app.services.data_ingest import save_index_statistics, save_stock_data, save_index_data, save_stock_predictions, save_stock_rank, save_stock_statistics
from app.repositories.indexes import get_any_date_index_price, get_last_index_days200_end_date, get_several_index_statistics, select_index_start_date, get_last_date_index_price, get_several_index_price, get_last_index_window_end_date
from app.repositories.stocks import get_any_date_stock_price, get_industry_stock_category, get_last_date_stock_price, get_last_stock_days200_end_date, get_last_stock_window_end_date, get_sector_stock_category, get_several_stock_price, get_several_stock_statistics, select_stock_start_date
from app.tasks.algorithm import calculate_stock_potensoial, days_index_moving_average, days_stock_moving_average, compute_rsi
from app.utils.app_state import get_tickers, get_model_params, get_user_db, get_sql_path
from app.tasks.predictions import destandardize_data, predict, standardize_index_data, standardize_stock_data, PredictionInput, PredictionInput_stock
from app.services.data_ingest import save_index_predictions
from app.routers.email import generate_stock_chart
from app.utils.file import open_sql_file

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
            # await asyncio.to_thread(save_index_statistics, data={}, ticker="^GSPC")
            # await asyncio.to_thread(save_index_predictions, data={}, ticker="^GSPC")
            await asyncio.to_thread(run_index_statistics_on_startup)
            await asyncio.to_thread(run_index_prediction_on_startup)
        else:
            print("⭕️ The index data is up to date in the financial database")
        if stock_start_date != end_date:
            await asyncio.to_thread(save_stock_data, get_tickers(), start_date=stock_start_date, end_date=end_date) # download and save in a thread to avoid blocking the event loop
            # await asyncio.to_thread(save_stock_statistics, data={}, ticker="^GSPC")
            # await asyncio.to_thread(save_stock_predictions, data={}, ticker="^GSPC")
            # await asyncio.to_thread(save_stock_rank, data={}, ticker=get_tickers()) 
            await asyncio.to_thread(run_stock_statistics_on_startup, get_tickers())
            await asyncio.to_thread(run_stock_prediction_on_startup, get_tickers()) 
            await asyncio.to_thread(run_stock_rank_on_startup, get_tickers())
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
        window_size = get_model_params("timesteps", ticker)
        last_days200_ma = get_several_index_statistics(symbols=[ticker], columns=['days200_ma'], limit=1)
        """
        # Skip prediction if no new data since last prediction
        if last_index_date == last_window_end_date:
            print(f"⭕️ Skipping index prediction, no new data since last prediction on {last_window_end_date}.")
            return
        """
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
        features = standardize_index_data(closes, volumes)

        # Create PredictionInput
        input_data = PredictionInput(features=features)

        # Run prediction
        result = predict(input_data, "^GSPC")
        
        # Data post-processing
        window_start_date = get_any_date_index_price(ticker, window_size)
        window_end_date = last_index_date
        predicted_scaled = np.array(result['prediction']).reshape(-1, 1)
        predicted_real = destandardize_data(predicted_scaled) # Destandardize predicted value
        last_actual_close = closes[-1, 0]
        recommendation = "BUY" if predicted_real >= last_days200_ma['days200_ma'][0] else "SELL"
        feature_number = get_model_params("num_features", ticker)
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
            window_size = get_model_params("timesteps", ticker)
            last_days200_ma = get_several_stock_statistics(symbols=[ticker], columns=['days200_ma'], limit=1)
            """
            # Skip prediction if no new data since last prediction
            if last_stock_date == last_window_end_date:
                print(f"⭕️ Skipping stock prediction, no new data since last prediction on {last_window_end_date}.")
                continue
            """
            # Get latest days(window size) of close and volume for ticker
            df = get_several_stock_price([ticker], ['close', 'volume'], limit=window_size)

            # Check data sufficiency
            if df.empty or len(df) < int(window_size):
                print(f"⚠️ Not enough stock data {ticker} for prediction (need {window_size} days)")
                continue
            
            # Prepare standardized features
            closes = df['close'].values.astype(float).reshape(-1, 1)
            rsi = compute_rsi(df['close'], period=14).fillna(0).to_numpy().astype(float).reshape(-1, 1)
            sma50 = df['close'].rolling(50).mean().fillna(0).to_numpy().astype(float).reshape(-1, 1)
            
            # Standardize data
            features = standardize_stock_data(closes, rsi, sma50)

            # Check if features are valid
            if features is None or not isinstance(features, (list, np.ndarray)) or len(features) == 0:
                print(f"⚠️ Features for {ticker} are invalid or empty. Skipping prediction.")
                return

            # Ensure features is a list
            if isinstance(features, np.ndarray):
                features = features.tolist()

            # Create PredictionInput_stock
            input_data = PredictionInput_stock(features=features)

            # Run prediction
            result = predict(input_data, ticker)
            
            # Data post-processing
            window_start_date = get_any_date_stock_price(ticker, window_size)
            window_end_date = last_stock_date
            predicted_scaled = np.array(result['prediction']).reshape(-1, 1)
            predicted_real = destandardize_data(predicted_scaled) # Destandardize predicted value
            last_actual_close = closes[-1, 0]
            recommendation = "BUY" if predicted_real >= last_days200_ma['days200_ma'][0] else "SELL"
            feature_number = get_model_params("num_features", ticker)
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
        for ticker in tickers:
            potential = calculate_stock_potensoial(ticker)
            print(f"potential: {potential}")
            if potential is not None:
                temp_po[ticker] = potential
            else:
                continue

        sorted_temp_po = {k: v for k, v in sorted(temp_po.items(), key=lambda item: item[1], reverse=True)}
        print(f"sorted_temp_po: {sorted_temp_po}")
            
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
            print(f"Potential: {potential}%")
    except Exception as e:
        print(f"❌ Error during startup stock ranking: {e}")

# Send scheduled email notifications
def send_scheduled_email_notifications():
    try:
        from app.utils.file import open_sql_file
        from app.utils.app_state import get_sql_path, get_user_db

        sender_email = "ifmapyishu3@gmail.com"
        sender_password = "wrvukaqqnzcszwge"

        # Get all emails that have bookmarks with notify=true and their notification settings
        sql_emails = open_sql_file(get_sql_path("select_emails_with_notify_bookmarks"))
        con = get_user_db()
        emails = con.execute(sql_emails).fetchall()

        for email_row in emails:
            email = email_row[0]  # Extract email from tuple
            sql_notification_setting = open_sql_file(get_sql_path("select_notification_setting"))
            notification_setting = con.execute(sql_notification_setting, (email,)).fetchone()
            if match_notification_time(notification_setting[0], notification_setting[3], notification_setting[1], notification_setting[2]):
                # Get all stock symbols for this email that have notify=true
                sql_bookmarks = open_sql_file(get_sql_path("select_notify_bookmarks_by_email"))
                bookmarks = con.execute(sql_bookmarks, (email,)).fetchall()
                for bookmark in bookmarks:
                    # Send email with stock chart for each bookmarked stock
                    try:
                        subject = f"Your Bookmark Notification--{bookmark[0]}"

                        message = MIMEMultipart("alternative")
                        message["From"] = sender_email
                        message["To"] = email
                        message["Subject"] = subject

                        html_body = f"""
                        <html>
                        <body>
                            <p>Dear User,</p>
                            <p>Here's your latest stock data for {bookmark[0]}:</p>
                            <img src="data:image/png;base64,{generate_stock_chart(bookmark[0])}" 
                            alt="{bookmark[0]} Chart" style="max-width:100%; height:auto;">
                            <p>Thank you for using our service!</p>
                        </body>
                        </html>
                        """
                        message.attach(MIMEText(html_body, "html"))

                        try:
                            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                                server.starttls()
                                server.login(sender_email, sender_password)
                                server.send_message(message)

                            print(f"Sending email to {email} successfully.")
                        except Exception as e:
                            raise HTTPException(status_code=500, detail=str(e))
                    except Exception as e:
                        print(f"❌ Error sending email to {email} for stock {bookmark[0]}: {e}")
            else:
                continue
           
            
        print(f"✅ Sent scheduled email notifications to {len(emails)} users")

    except Exception as e:
        print(f"❌ Error during scheduled email notifications: {e}")

def match_notification_time(frequency: str, notification_time: str, day_of_week: str = None, date: int = None) -> bool:
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    if frequency == "daily":
        return current_time == notification_time
    elif frequency == "weekly":
        current_day_of_week = datetime.now().strftime("%A")
        return current_time == notification_time and current_day_of_week == day_of_week
    elif frequency == "monthly":
        current_date = datetime.now().day
        # check current month has the specified date, if not, use the last day of the month
        last_day_of_month = (datetime(now.year, now.month + 1, 1) - timedelta(days=1)).day
        if date > last_day_of_month:            
            date = last_day_of_month
        return current_time == notification_time and current_date == date
    else:
        return False