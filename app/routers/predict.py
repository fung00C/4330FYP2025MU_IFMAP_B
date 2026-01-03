# app/routers/predict.py
from fastapi import APIRouter, HTTPException, Query

from app.repositories.stocks import get_stock_detail

router = APIRouter(prefix="/predict", tags=["predict"])

@router.get("/stock")
async def api_get_stock_prediction(
    symbol: str = Query('AAPL', description="股票代碼，例如 'AAPL', 'MSFT'"),
):
    """
    Get a stock prediction data
    """
    pass

@router.get("/index")
async def api_get_index_prediction(
    symbol: str = Query('^GSPC', description="指數代碼，例如 '^GSPC'"),
):
    """
    Get a index prediction data
    """
    try:
         # 輸入驗證
        if not symbol:
            raise HTTPException(status_code=404, detail=f"symbols must not be empty")
        """df = get_stock_detail(
            symbol=symbol
        )
        result = df.to_dict(orient="records") # 將 DataFrame 轉為 JSON 格式輸出
        return {"search": symbol, "data": result}"""
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
