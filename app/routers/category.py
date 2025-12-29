# app/routers/stock_category.py

from fastapi import APIRouter, HTTPException

from app.repositories.stocks import get_stock_category

router = APIRouter(prefix="/category", tags=["category"])

@router.get("/stock")
async def api_get_stock_category():
    """
    Get all stock category data
    """
    try:
        #raise HTTPException(status_code=404, detail=f"symbols must not be empty")
        df = get_stock_category()
        result = df.to_dict(orient="records") # 將 DataFrame 轉為 JSON 格式輸出

        # TODO: make 'result' to the json fromat like: [{sector: {industry: [symbols]}}, ...]


        return {"data type": "json", "number of sector": len(), "number of industry": len(),  "data": "new format data"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/index")
async def api_get_index_category():
    """
    Get all index category data
    """

    return 