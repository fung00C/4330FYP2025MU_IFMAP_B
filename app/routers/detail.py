# app/routers/stock_detail.py
from fastapi import APIRouter, HTTPException, Query

from app.repositories.stocks import get_stock_detail

router = APIRouter(prefix="/detail", tags=["detail"])

@router.get("/stock")
async def api_get_stock_detail(
    symbol: str = Query('AAPL', description="股票代碼，例如 'AAPL', 'MSFT'"),
):
    """
    Get a stock detail data
    """
    try:
         # 輸入驗證
        if not symbol:
            raise HTTPException(status_code=404, detail=f"symbols must not be empty")
        df = get_stock_detail(
            symbol=symbol
        )
        result = df.to_dict(orient="records") # 將 DataFrame 轉為 JSON 格式輸出
        return {"search": symbol, "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index")
async def api_get_index_detail():
    """
    Get a index detail data
    """

    return 