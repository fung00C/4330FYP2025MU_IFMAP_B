# app/routers/stock_category.py

from fastapi import APIRouter

router = APIRouter(prefix="/category", tags=["category"])

@router.get("/stock")
async def api_get_stock_category():
    """get all stock category data"""

    return 

@router.get("/index")
async def api_get_index_category():
    """get all index category data"""

    return 