# app/repositories/indexes.py
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException

from app.utils.app_state import get_fin_db, get_sql_path, FIXED_COLUMNS_IN_FINANCIAL
from app.utils.file import open_sql_file

# read financial.db to get the number of lasted data in a index_price table
def get_index_all_price(symbols: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, limit: Optional[int] = None) -> pd.DataFrame:
    """
    從統一的 index_price 表中查詢一支或多隻指數的全部資料。
    :param symbols: 指數代碼列表，例如 ["^GSPC"]
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 結束日期 (YYYY-MM-DD)
    :param limit: 最大返回筆數
    :return: 查詢結果 DataFrame
    """
    # 載入查詢模板
    sql_template = open_sql_file(get_sql_path('select_all_index_price'))
        
    # 動態產生 IN 子句問號（參數化避免注入）
    placeholders = ",".join(["?"] * len(symbols))
    symbol_clause = f"AND symbol IN ({placeholders})"
    sql_template = sql_template.replace("/*SYMBOL_IN_CLAUSE*/", f"\n  {symbol_clause}")

    # 可選日期條件（用參數佔位符，值放在 params）
    params: List[object] = []
    params.extend(symbols)
    if start_date:
        sql_template = sql_template.replace("/*DATE_START_COND*/", "AND date >= ?")
        params.append(start_date)
    else:
        sql_template = sql_template.replace("/*DATE_START_COND*/", "")
    if end_date:
        sql_template = sql_template.replace("/*DATE_END_COND*/", "AND date <= ?")
        params.append(end_date)
    else:
        sql_template = sql_template.replace("/*DATE_END_COND*/", "")
    if limit:
        sql_template = sql_template.replace("/*DATA_LIMIT*/", "LIMIT ?")
        params.append(limit) # LIMIT 放在模板最後一個 ?，加入參數
    else:
        sql_template = sql_template.replace("/*DATA_LIMIT*/", "")

    try:
        df = pd.read_sql_query(sql=sql_template, con=get_fin_db(), params=params) # 用 pd.read_sql_query(sql, conn, params=params) 直接回傳 DataFrame
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for requested symbols.")
        print(f"✅ Retrieved {len(df)} rows for {symbols}")
        return df
    except Exception as e:
        print(f"❌ Error retrieving stock {e}")
        raise HTTPException(status_code=500, detail=str(e))

# read financial.db to get several column date stored in index_price table
def get_several_index_price(symbols: List[str], columns: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, limit: Optional[int] = None):
    """
    從統一的 index_price 表中查詢一支或多支指數的不同價格資料。
    :param symbols: 指數代碼列表，例如 ["^GSPC"]
    :param columns: 數據欄列表，例如 ["open", "close"]
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 結束日期 (YYYY-MM-DD)
    :param limit: 最大返回筆數
    :return: 查詢結果 DataFrame
    """
    sql_template = open_sql_file(get_sql_path('select_several_index_price'))
    select_cols = ", ".join(FIXED_COLUMNS_IN_FINANCIAL + columns)  # 以字串插入識別字（不能用參數化）
    sql_template = sql_template.replace("/*SELECT_COLUMNS*/", select_cols)
    placeholders = ",".join(["?"] * len(symbols)) # 值條件一律參數化
    sql_template = sql_template.replace("/*SYMBOL_IN_CLAUSE*/", f"AND symbol IN ({placeholders})")
    params: List[object] = list(symbols)
    if start_date:
        sql_template = sql_template.replace("/*DATE_START_COND*/", "AND date >= ?")
        params.append(start_date)
    else:
        sql_template = sql_template.replace("/*DATE_START_COND*/", "")
    if end_date:
        sql_template = sql_template.replace("/*DATE_END_COND*/", "AND date <= ?")
        params.append(end_date)
    else:
        sql_template = sql_template.replace("/*DATE_END_COND*/", "")
    if limit:
        sql_template = sql_template.replace("/*DATA_LIMIT*/", "LIMIT ?")
        params.append(limit)
    else:
        sql_template = sql_template.replace("/*DATA_LIMIT*/", "")
    try:
        df = pd.read_sql_query(sql=sql_template, con=get_fin_db(), params=params)  # 只綁值，不綁欄位名
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for requested symbols.")
        print(f"✅ Retrieved {len(df)} rows of prices({columns}) for {symbols}")
        return df
    except Exception as e:
        print(f"❌ Error retrieving stock {e}")
        raise HTTPException(status_code=500, detail=str(e))

# read financial.db to get last date stored in index_price table and return the next date as start_date
def select_index_start_date(database: str = "financial.db"):
    start_date = ""
    try:
        cursor = get_fin_db().cursor()
        sql_template = open_sql_file(get_sql_path("select_last_date_index_price"))
        cursor.execute(sql_template)
        row = cursor.fetchone()
        if row and row[0]:
            last_date = datetime.fromisoformat(row[0]) # assume stored dates are in YYYY-MM-DD format
            start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
            print(f"✅ Last stored date (index) fetched from database '{database}' and next start date is '{start_date}'")
        else:
            start_date = "2015-01-01" # fallback default start date if no data present
            print(f"✅ No existing data found in index_price table, using default start date '{start_date}'")
        return start_date
    except Exception as e:
        print(f"❌ Could not determine last stored date (index), falling back to default. Error: {e}")
        return "2015-01-01"

# read financial.db to get last date stored in index_price table
def get_last_index_date(database: str = "financial.db"):
    last_date = ""
    try:
        cursor = get_fin_db().cursor()
        sql_template = open_sql_file(get_sql_path("select_last_date_index_price"))
        cursor.execute(sql_template)
        row = cursor.fetchone()
        #last_date = datetime.fromisoformat(row[0])#.strftime("%Y-%m-%d")
        last_date = row[0]
        print(f"✅ Last stored date (index) fetched from database '{database}'")
        return last_date
    except Exception as e:
        print(f"❌ Could not determine last stored date (index), falling back to default. Error: {e}")
        return ""
    
# read financial.db to get last window_end_date stored in index_predictions table
def get_last_index_window_end_date(database: str = "financial.db"):
    last_window_end_date = ""
    try:
        cursor = get_fin_db().cursor()
        sql_template = open_sql_file(get_sql_path("select_last_date_index_predictions"))
        cursor.execute(sql_template)
        row = cursor.fetchone()
        #last_window_end_date = datetime.fromisoformat(row[0])#.strftime("%Y-%m-%d")
        last_window_end_date = row[0]
        print(f"✅ Last window end date from index_predictions fetched from database '{database}'")
        return last_window_end_date
    except Exception as e:
        print(f"❌ Could not determine last window end date from index_predictions, falling back to default. Error: {e}")
        return ""

# read financial.db to get any date with offset and any ticker stored in index_price table
def get_any_index_date(ticker: str, offset: int, database: str = "financial.db"):
    date = ""
    try:
        cursor = get_fin_db().cursor()
        sql_template = open_sql_file(get_sql_path("select_any_date_index_price"))
        cursor.execute(sql_template, (ticker, (offset - 1))) # OFFSET window_size - 1 to get the Nth(window_size) record
        row = cursor.fetchone()
        date = row[0] if row else ""
        print(f"✅ Fetched date with offset {offset} for {ticker} from database '{database}'")
        return date
    except Exception as e:
        print(f"❌ Could not fetch date with offset {offset} for {ticker}, falling back to default. Error: {e}")
        return ""
    
# read financial.db to get range of close price stored in index_price table
def get_range_index_close_price(ticker: str, limit: int):
    """
    從 index_price 表中查詢指定指數的收盤價資料，限制返回筆數。
    :param ticker: 指數代碼，例如 "^GSPC"
    :param limit: 返回的最大筆數
    :return: 查詢結果 DataFrame
    """
    sql_template = open_sql_file(get_sql_path("select_range_index_close_price"))
    params = (ticker, limit)
    try:
        df = pd.read_sql_query(sql=sql_template, con=get_fin_db(), params=params)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No close price data found for ticker: {ticker}")
        print(f"✅ Retrieved {len(df)} rows of close prices for {ticker}")
        return df
    except Exception as e:
        print(f"❌ Error retrieving range of close prices for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
def get_index_detail(symbol: str):
    """
    從 index_detail 表中查詢單一股票的詳細資料。
    :param symbol: 股票代碼，例如 "^GSPC"
    :return: 查詢結果 DataFrame
    """
    pass

def get_index_category():
    """
    從 index_detail 表中查詢所有股票的分類資料。
    :return: 查詢結果 DataFrame
    """
    pass

def get_predicted_data_index():
    pass