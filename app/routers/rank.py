# app/routers/rank.py
from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.repositories.stocks import get_serveral_stock_rank

router = APIRouter(prefix="/rank", tags=["rank"])

@router.get("/stock")
async def api_get_stock_rank(
    symbol: List[str] = Query(['AAPL'], description="股票代碼，例如 'AAPL', 'MSFT'"),
):
    """
    Get a specific stock recommendation data
    """
    try:
        # 輸入驗證
        if not symbol:
            raise HTTPException(status_code=404, detail=f"symbols must not be empty")
        df = get_serveral_stock_rank(symbols=symbol, columns=['symbol', 'industry', 'current_price', 'potential'], limit=1)
        result = df.to_dict(orient="records") # 將 DataFrame 轉為 JSON 格式輸出
        return {"search": symbol, "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
