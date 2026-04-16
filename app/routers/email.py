# app/routers/email.py

from fastapi import APIRouter, HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from io import BytesIO
from datetime import datetime, timedelta
import plotly.graph_objects as go
import base64

from app.repositories.stocks import get_several_stock_price

router = APIRouter(prefix="/email", tags=["email"])

sender_email = "ifmapyishu3@gmail.com"
sender_password = "wrvukaqqnzcszwge"

@router.post("/send")
async def api_send_email(
    email: str,
):
    receiver_email = email
    subject = "Your Bookmark Notification"

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    html_body = f"""
    <html>
    <body>
        <h2>Your Stocks Update</h2>
        <p>Here's your latest stock data:</p>
        <img src="data:image/png;base64,{generate_stock_chart('AAPL')}" 
             alt="AAPL Chart" style="max-width:100%; height:auto;">
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
        return {"message": f"Email sent to {email} successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def generate_stock_chart(
        symbol: str,
):
    end_date = datetime.utcnow().date()
    start_date = (end_date - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    df = get_several_stock_price(
        symbols=[symbol],
        columns=["open", "high", "low", "close"],
        start_date=start_date,
        end_date=end_date_str,
    )

    if df.empty:
        raise ValueError("No stock price data available for the specified symbol and date range.")

    fig = go.Figure(data=[go.Candlestick(x=df.index,
        open=df['open'], high=df['high'],
        low=df['low'], close=df['close'])])
    
    fig.update_layout(title=f"{symbol} Price (Past Month)",
                      yaxis_title="Price",
                      xaxis_title="Date",
                      height=500)
    
    # Convert to base64 PNG
    img_bytes = fig.to_image(format="png", width=800, height=500)
    return base64.b64encode(img_bytes).decode()