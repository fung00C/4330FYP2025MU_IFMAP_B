# app/routers/tickers.py
from fastapi import APIRouter
from app.repositories.meta import get_ticker_symbols
from app.utils.app_state import get_tickers

router = APIRouter(prefix="/ticker-symbols", tags=["tickers"])

@router.get("/")
async def api_get_ticker_symbols():
    """get all ticker symbols"""
    symbols = get_tickers()
    return {"tickers": symbols}
