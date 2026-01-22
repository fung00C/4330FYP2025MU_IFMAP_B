# app/tasks/technical_indicator.py
from app.repositories.indexes import get_range_index_close_price
from app.repositories.stocks import get_several_stock_predictions, get_several_stock_price

# Calculate index moving average for given days
def days_index_moving_average(ticker: str = "^GSPC", days: int = 0):
    df = get_range_index_close_price(ticker, days)
    if df.empty or len(df) < days:
        print(f"⚠️ Not enough data for {ticker} to calculate {days}-day moving average")
        return None
    moving_average = df['close'].astype(float).mean()
    print(f"✅ Calculated {days}-day moving average for {ticker}: {moving_average}")
    return moving_average

# Calculate stock moving average for given days
def days_stock_moving_average(ticker: str, days: int):
    df = get_several_stock_price(symbols=[ticker], columns=['close'], limit=days)
    if df.empty or len(df) < days:
        print(f"⚠️ Not enough data for {ticker} to calculate {days}-day moving average")
        return None
    moving_average = df['close'].astype(float).mean()
    print(f"✅ Calculated {days}-day moving average for {ticker}: {moving_average}")
    return moving_average

# Claculate stock potential based on predicted price and 200-day moving average
def calculate_stock_potensoial(ticker:str):
    predicted_price = get_several_stock_predictions(symbols=[ticker], columns=['predicted_real'], limit=1)['predicted_real'][0]
    ma_200 = days_stock_moving_average(ticker, 200)
    if predicted_price is None or ma_200 is None:
        print(f"⚠️ Cannot calculate potential for {ticker} due to missing data")
        return None
    potential = (predicted_price - ma_200) / ma_200 * 100
    print(f"✅ Calculated stock potential for {ticker}: {potential}%")
    return potential