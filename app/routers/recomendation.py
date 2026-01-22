# app/routers/recommendation.py
from typing import List
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from app.repositories.indexes import get_several_index_predictions, get_several_index_statistics

router = APIRouter(prefix="/recommendation", tags=["recommendation"])

@router.get("/stock")
async def api_get_stock_prediction(
    symbol: List[str] = Query(['AAPL'], description="股票代碼，例如 'AAPL', 'MSFT'"),
):
    """
    Get a specific stock recommendation data
    """
    pass

@router.get("/index")
async def api_get_index_prediction(
    symbol: List[str] = Query(['^GSPC'], description="指數代碼，例如 ['^GSPC']"),
):
    """
    Get a specific index recommendation data
    """
    try:
        # 輸入驗證
        if not symbol:
            raise HTTPException(status_code=404, detail=f"symbols must not be empty")
        df_st = get_several_index_statistics(symbols=symbol, columns=['days200_ma'], limit=1)
        df_pd = get_several_index_predictions(symbols=symbol, columns=['predicted_real', 'recommendation'], limit=1)
        df = pd.concat([df_st, df_pd], axis=1)
        result = df.to_dict(orient="records") # 將 DataFrame 轉為 JSON 格式輸出
        return {"search": symbol, "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
