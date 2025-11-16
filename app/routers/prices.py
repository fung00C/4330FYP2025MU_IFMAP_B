# app/routers/prices.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.repositories.indexes import get_index_all_price, get_several_index_price
from app.repositories.stocks import get_stock_all_price, get_several_stock_price
from app.utils.app_state import ALLOWED_COLUMNS_IN_FINANCIAL

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("/index/query-all")
def query_all_index_data(
    symbols: List[str] = Query(['^GSPC'], description="指數代碼，例如 ['^GSPC']"),
    start_date: Optional[str] = Query(None, description="起始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="結束日期 (YYYY-MM-DD)"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="返回筆數上限，預設關閉")
):
    """
    從統一的 index_price 資料表查詢多隻指數的全部歷史價格資料。
    支援日期篩選與筆數限制。
    """
    try:
        if not symbols:
            raise ValueError("symbols must not be empty")
        df = get_index_all_price(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        result = df.to_dict(orient="records") # 將 DataFrame 轉為 JSON 格式輸出
        return {"count": len(result), "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/query-all")
def query_all_stock_data(
    symbols: List[str] = Query(['AAPL'], description="股票代碼，例如 ['AAPL', 'MSFT']"),
    start_date: Optional[str] = Query(None, description="起始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="結束日期 (YYYY-MM-DD)"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="返回筆數上限，預設關閉")
):
    """
    從統一的 stock_price 資料表查詢多支股票的全部歷史價格資料。
    支援日期篩選與筆數限制。
    """
    try:
        if not symbols:
            raise ValueError("symbols must not be empty")
        df = get_stock_all_price(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        result = df.to_dict(orient="records") # 將 DataFrame 轉為 JSON 格式輸出
        return {"count": len(result), "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index/query-several")
def query_several_index_data(
    symbols: List[str] = Query(['^GSPC'], description="指數代碼，例如 ['^GSPC']"),
    columns: List[str] = Query(['close'], description="指數價格種類，例如 ['open', 'close']"),
    start_date: Optional[str] = Query(None, description="起始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="結束日期 (YYYY-MM-DD)"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="返回筆數上限，預設關閉")
):
    """
    從統一的 index_price 資料表查詢多支指數不同價格的歷史資料。
    支援日期篩選與筆數限制。
    """
    try:
         # 輸入驗證
        if not symbols:
            raise HTTPException(status_code=404, detail=f"symbols must not be empty")
        if not columns:
            raise HTTPException(status_code=404, detail=f"column must not be empty")
        # 驗證識別字
        for c in columns:
            if c not in ALLOWED_COLUMNS_IN_FINANCIAL:
                raise HTTPException(status_code=404, detail=f"nvalid column: {c}")
        df = get_several_index_price(
            symbols=symbols,
            columns=columns,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        result = df.to_dict(orient="records") # 將 DataFrame 轉為 JSON 格式輸出
        return {"count": len(result), "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/query-several")
def query_several_stock_data(
    symbols: List[str] = Query(['AAPL'], description="股票代碼，例如 ['AAPL', 'MSFT']"),
    columns: List[str] = Query(['close'], description="股票價格種類，例如 ['open', 'close']"),
    start_date: Optional[str] = Query(None, description="起始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="結束日期 (YYYY-MM-DD)"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="返回筆數上限，預設關閉")
):
    """
    從統一的 stock_price 資料表查詢多支股票不同價格的歷史資料。
    支援日期篩選與筆數限制。
    """
    try:
         # 輸入驗證
        if not symbols:
            raise HTTPException(status_code=404, detail=f"symbols must not be empty")
        if not columns:
            raise HTTPException(status_code=404, detail=f"column must not be empty")
        # 驗證識別字
        for c in columns:
            if c not in ALLOWED_COLUMNS_IN_FINANCIAL:
                raise HTTPException(status_code=404, detail=f"nvalid column: {c}")
        df = get_several_stock_price(
            symbols=symbols,
            columns=columns,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        result = df.to_dict(orient="records") # 將 DataFrame 轉為 JSON 格式輸出
        return {"count": len(result), "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
