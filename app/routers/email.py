# app/routers/email.py

from fastapi import APIRouter, HTTPException, Query
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(prefix="/email", tags=["email"])

sender_email = "ifmapyishu3@gmail.com"
sender_password = "wrvukaqqnzcszwge"

@router.post("/send")
async def api_asend_email(
    email: str,
): 
    receiver_email = email
    
    subject = "Stock Alert"
    body = "This is a stock alert email."
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        print(f"Sending email to {email} successfully.")
        return {"message": f"Email sent to {email} successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))