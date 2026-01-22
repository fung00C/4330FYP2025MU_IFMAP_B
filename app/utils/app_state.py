# app/utils/app_state.py
from typing import Optional, List
import sqlite3
import threading
import time

# index_piece and stock_price table column name
ALLOWED_COLUMNS_IN_FINANCIAL = {"open","high","low","close","volume"}  # 白名單
FIXED_COLUMNS_IN_FINANCIAL = ["symbol","date"]

# SQL file paths
sql_file_create_index_price_table = 'app/db/sql/create_index_price_table.sql'
sql_file_create_stock_price_table = 'app/db/sql/create_stock_price_table.sql'
sql_file_create_index_predictions_table = 'app/db/sql/create_index_predictions_table.sql'
sql_file_create_stock_predictions_table = 'app/db/sql/create_stock_predictions_table.sql'
sql_file_create_index_statistics_table = 'app/db/sql/create_index_statistics_table.sql'
sql_file_create_stock_statistics_table = 'app/db/sql/create_stock_statistics_table.sql'
sql_file_create_stock_rank_table = 'app/db/sql/create_stock_rank_table.sql'
sql_file_create_user_table = 'app/db/sql/create_user_table.sql'
sql_file_drop_index_price_table = 'app/db/sql/drop_index_price_table.sql'
sql_file_drop_stock_price_table = 'app/db/sql/drop_stock_price_table.sql'
sql_file_drop_index_predictions_table = 'app/db/sql/drop_index_predictions_table.sql'
sql_file_drop_stock_predictions_table = 'app/db/sql/drop_stock_predictions_table.sql'
sql_file_drop_index_statistics_table = 'app/db/sql/drop_index_statistics_table.sql'
sql_file_drop_stock_statistics_table = 'app/db/sql/drop_stock_statistics_table.sql'
sql_file_drop_stock_rank_table = 'app/db/sql/drop_stock_rank_table.sql'
sql_file_select_symbol_stock_detail = 'app/db/sql/select_symbol_stock_detail.sql'
sql_file_select_table_name_financial = 'app/db/sql/select_table_name_financial.sql'
sql_file_select_last_date_index_price = 'app/db/sql/select_last_date_index_price.sql'
sql_file_select_last_wedate_index_predictions = 'app/db/sql/select_last_wedate_index_predictions.sql'
sql_file_select_last_wedate_stock_predictions = 'app/db/sql/select_last_wedate_stock_predictions.sql'
sql_file_select_last_d200edate_index_statistics = 'app/db/sql/select_last_d200edate_index_statistics.sql'
sql_file_select_last_d200edate_stock_statistics = 'app/db/sql/select_last_d200edate_stock_statistics.sql'
sql_file_select_any_date_index_price = 'app/db/sql/select_any_date_index_price.sql'
sql_file_select_any_date_stock_price = 'app/db/sql/select_any_date_stock_price.sql'
sql_file_select_last_date_stock_price = 'app/db/sql/select_last_date_stock_price.sql'
sql_file_select_last_date_stock_predictions = 'app/db/sql/select_last_date_stock_predictions.sql'
sql_file_select_all_stock_price = 'app/db/sql/select_all_stock_price.sql'
sql_file_select_all_index_price = 'app/db/sql/select_all_index_price.sql'
sql_file_select_several_index_price = 'app/db/sql/select_several_index_price.sql'
sql_file_select_several_stock_price = 'app/db/sql/select_several_stock_price.sql'
sql_file_select_several_index_statistics = 'app/db/sql/select_several_index_statistics.sql'
sql_file_select_several_stock_statistics = 'app/db/sql/select_several_stock_statistics.sql'
sql_file_select_several_index_predictions = 'app/db/sql/select_several_index_predictions.sql'
sql_file_select_several_stock_predictions = 'app/db/sql/select_several_stock_predictions.sql'
sql_file_select_several_stock_rank = 'app/db/sql/select_several_stock_rank.sql'
sql_file_select_detail_stock_detail = 'app/db/sql/select_detail_stock_detail.sql'
sql_file_select_category_stock_detail = 'app/db/sql/select_category_stock_detail.sql'
sql_file_insert_index_predictions_data = 'app/db/sql/insert_index_predictions_data.sql'
sql_file_insert_stock_predictions_data = 'app/db/sql/insert_stock_predictions_data.sql'
sql_file_insert_index_statistics_data = 'app/db/sql/insert_index_statistics_data.sql'
sql_file_insert_stock_statistics_data = 'app/db/sql/insert_stock_statistics_data.sql'
sql_file_insert_stock_rank_data = 'app/db/sql/insert_stock_rank_data.sql'

# database variables
_fin_db: Optional[sqlite3.Connection] = None
_user_db: Optional[sqlite3.Connection] = None

# ticker cache
_tickers: Optional[List[str]] = None
_tickers_lock = threading.Lock()
_tickers_last_updated: Optional[float] = None

# statistics cache
_statistics_last_updated: str = ""

# predictions cache
_predictions_last_updated: str = ""

# model
_model: Optional[any] = None

# model variables
_input_shape = None
_timesteps = None
_num_features = None
_total_inputs = None
_data_type = None

def get_sql_path(arg) -> Optional[str]:
    match arg:
        case 'create_index_price_table':
            return sql_file_create_index_price_table
        case 'create_stock_price_table':
            return sql_file_create_stock_price_table
        case 'create_index_predictions_table':
            return sql_file_create_index_predictions_table
        case 'create_stock_predictions_table':
            return sql_file_create_stock_predictions_table
        case 'create_index_statistics_table':
            return sql_file_create_index_statistics_table
        case 'create_stock_statistics_table':
            return sql_file_create_stock_statistics_table
        case 'create_stock_rank_table':
            return sql_file_create_stock_rank_table
        case 'create_user_table':
            return sql_file_create_user_table
        case 'drop_index_price_table':
            return sql_file_drop_index_price_table
        case 'drop_stock_price_table':
            return sql_file_drop_stock_price_table
        case 'drop_index_predictions_table':
            return sql_file_drop_index_predictions_table
        case 'drop_stock_predictions_table':
            return sql_file_drop_stock_predictions_table
        case 'drop_index_statistics_table':
            return sql_file_drop_index_statistics_table
        case 'drop_stock_statistics_table':
            return sql_file_drop_stock_statistics_table
        case 'drop_stock_rank_table':
            return sql_file_drop_stock_rank_table
        case 'select_symbol_stock_detail':
            return sql_file_select_symbol_stock_detail
        case 'select_table_name_financial':
            return sql_file_select_table_name_financial
        case 'select_last_date_index_price':
            return sql_file_select_last_date_index_price
        case 'select_last_wedate_index_predictions':
            return sql_file_select_last_wedate_index_predictions
        case 'select_last_wedate_stock_predictions':
            return sql_file_select_last_wedate_stock_predictions
        case 'select_last_d200edate_index_statistics':
            return sql_file_select_last_d200edate_index_statistics
        case 'select_last_d200edate_stock_statistics':
            return sql_file_select_last_d200edate_stock_statistics
        case 'select_any_date_index_price':
            return sql_file_select_any_date_index_price
        case 'select_any_date_stock_price':
            return sql_file_select_any_date_stock_price
        case 'select_last_date_stock_price':
            return sql_file_select_last_date_stock_price
        case 'select_last_date_stock_predictions':
            return sql_file_select_last_date_stock_predictions
        case 'select_all_stock_price':
            return sql_file_select_all_stock_price
        case 'select_all_index_price':
            return sql_file_select_all_index_price
        case 'select_several_stock_price':
            return sql_file_select_several_stock_price
        case 'select_several_index_price':
            return sql_file_select_several_index_price
        case 'select_several_index_statistics':
            return sql_file_select_several_index_statistics
        case 'select_several_stock_statistics':
            return sql_file_select_several_stock_statistics
        case 'select_several_index_predictions':
            return sql_file_select_several_index_predictions
        case 'select_several_stock_predictions':
            return sql_file_select_several_stock_predictions
        case 'select_several_stock_rank':
            return sql_file_select_several_stock_rank
        case 'select_detail_stock_detail':
            return sql_file_select_detail_stock_detail
        case 'select_category_stock_detail':
            return sql_file_select_category_stock_detail
        case 'insert_index_predictions_data':
            return sql_file_insert_index_predictions_data
        case 'insert_stock_predictions_data':
            return sql_file_insert_stock_predictions_data
        case 'insert_index_statistics_data':
            return sql_file_insert_index_statistics_data
        case 'insert_stock_statistics_data':
            return sql_file_insert_stock_statistics_data
        case 'insert_stock_rank_data':
            return sql_file_insert_stock_rank_data
        case _:
            return None

def set_fin_db(conn: sqlite3.Connection) -> None:
    global _fin_db
    _fin_db = conn

def get_fin_db() -> sqlite3.Connection:
    if _fin_db is None:
        raise RuntimeError("⚠️ fin_db is not initialized")
    return _fin_db

def set_user_db(conn: sqlite3.Connection) -> None:
    global _user_db
    _user_db = conn

def get_user_db() -> sqlite3.Connection:
    if _user_db is None:
        raise RuntimeError("⚠️ user_db is not initialized")
    return _user_db

def set_tickers(tickers: List[str]) -> None:
    """Set the global ticker list (thread-safe)."""
    global _tickers, _tickers_last_updated
    with _tickers_lock:
        # store a shallow copy to avoid external mutation
        _tickers = list(tickers) if tickers is not None else []
        _tickers_last_updated = time.time()

def get_tickers() -> List[str]:
    """Return the cached tickers. If not initialized, returns an empty list."""
    with _tickers_lock:
        if _tickers is None:
            return []
        return list(_tickers)

def get_tickers_last_updated() -> Optional[float]:
    """Return epoch timestamp of last tickers update, or None if never set."""
    with _tickers_lock:
        return _tickers_last_updated
    
def set_statistics_last_updated(timestamp: str) -> None:
    global _statistics_last_updated
    _statistics_last_updated = timestamp

def get_statistics_last_updated() -> str:
    return _statistics_last_updated

def set_predictions_last_updated(timestamp: str) -> None:
    global _predictions_last_updated
    _predictions_last_updated = timestamp

def get_predictions_last_updated() -> str:
    return _predictions_last_updated

def set_model_params(timesteps, num_features, total_inputs) -> None:
    global _timesteps, _num_features, _total_inputs
    _timesteps = timesteps
    _num_features = num_features
    _total_inputs = total_inputs

def get_model_params(arg) -> Optional[str]:
    match arg:
        case 'timesteps':
            return _timesteps
        case 'num_features':
            return _num_features
        case 'total_inputs':
            return _total_inputs
        case _:
            return None
        
def set_model(model_instance) -> None:
    global _model
    _model = model_instance

def get_model():
    return _model