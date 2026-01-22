# app/tasks/technical_indicator.py
from app.repositories.indexes import get_range_index_close_price

# Calculate moving average for given days
def days_moving_average(ticker: str = "^GSPC", days: int = 0):
    df = get_range_index_close_price(ticker, days)
    if df.empty or len(df) < days:
        print(f"⚠️ Not enough data for {ticker} to calculate {days}-day moving average")
        return None
    moving_average = df['close'].astype(float).mean()
    print(f"✅ Calculated {days}-day moving average for {ticker}: {moving_average}")
    return moving_average