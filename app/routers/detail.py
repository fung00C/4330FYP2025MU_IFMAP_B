# app/routers/stock_detail.py

from fastapi import APIRouter, HTTPException, Query

from app.repositories.stocks import get_stock_detail

router = APIRouter(prefix="/detail", tags=["detail"])

@router.get("/stock")
async def api_get_stock_detail(
    symbol: str = Query('AAPL', description="股票代碼，例如 'AAPL', 'MSFT'"),
):
    """
    Get a specific stock detail data
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
async def api_get_index_detail(
    symbol: str = Query('^GSPC', description="指數代碼，例如 '^GSPC'"),
):
    """
    Get a specific index detail data
    """
    try:
        # 輸入驗證
        if not symbol:
            raise HTTPException(status_code=404, detail=f"symbols must not be empty")
        result = [{
            "Composition": "500 major U.S. companies, though sometimes slightly more due to multiple share classes (e.g., Alphabet).",
            "Weighting": "Market-cap weighted, meaning larger companies by market value have a greater impact on the index's value.",
            "Purpose": "A leading indicator of U.S. stock market performance and economic health.",
            "Management": "Maintained by S&P Dow Jones Indices.",
            "Accessibility": "You can't invest directly, but through index funds (ETFs/mutual funds) that track it, such as SPY, VOO.",
            "Sectors": "Includes companies from all major U.S. industries like tech, financials, healthcare, etc.."
        }]
        return {"search": symbol, "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 