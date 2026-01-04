# app/routers/stock_category.py

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.repositories.stocks import get_stock_category

router = APIRouter(prefix="/category", tags=["category"])

@router.get("/stock")
async def api_get_stock_category():
    """
    Get all stock category data
    """
    try:
        json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'json', 'stock_category.json')
        if not os.path.exists(json_path):
            raise HTTPException(status_code=404, detail="Stock category JSON file not found")
        return FileResponse(path=json_path, media_type='application/json')
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""@router.get("/index")
async def api_get_index_category():
    ""
    Get all index category data
    ""
    pass"""