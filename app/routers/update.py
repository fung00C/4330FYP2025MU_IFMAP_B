# app/routers/update.py
from fastapi import APIRouter
from app.tasks.jobs import update_financial_data_job

router = APIRouter(prefix="/update", tags=["update"])

@router.post("/")
async def api_update_stock_data():
    """manually update the financial database"""
    await update_financial_data_job("manual")
    return {"message": "complete an update of the financial database"}