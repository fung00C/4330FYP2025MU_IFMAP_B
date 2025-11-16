# app/routers/tables.py
from fastapi import APIRouter
from app.repositories.meta import get_stock_tables

router = APIRouter(prefix="/tables", tags=["tables"])

@router.get("/")
async def api_get_stock_tables():
    """get all stock table names"""
    tables = get_stock_tables()
    return {"tables": tables}
