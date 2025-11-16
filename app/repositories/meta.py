# app/repositories/meta.py
from app.utils.app_state import get_fin_db, get_sql_path
from app.utils.file import open_sql_file

# create a table
def create_table(db, table_name, sql_template: str):
    try:
        cursor = db.cursor()
        cursor.executescript(sql_template)
        db.commit()
        print(f"✅ {table_name} table initialized successfully.")
    except Exception as e:
        print(f"❌ An error occurred while creating table {table_name}: {e}")

# drop a table
def drop_table(db, table_name, sql_template: str):
    try:
        cursor = db.cursor()
        cursor.executescript(sql_template)
        db.commit()
        print(f"✅ {table_name} table dropped successfully.")
    except Exception as e:
        print(f"❌ An error occurred while dropping table {table_name}: {e}")

# get ticker symbol from financial.db stock_detail table
def get_ticker_symbols():
    ticker_symbols = []
    try:
        cursor = get_fin_db().cursor()
        sql_template = open_sql_file(get_sql_path("select_symbol_stock_detail"))
        cursor.execute(sql_template)
        rows = cursor.fetchall()
        ticker_symbols = [row[0] for row in rows]
        #print(f"Ticker symbols fetched from stock_detail table: {ticker_symbols}")
        print("✅ Ticker symbols fetched from stock_detail table.")
        return ticker_symbols
    except Exception as e:
        print(f"❌ An error occurred while fetching ticker symbols: {e}")
        return []

# read financial.db to get all table names
def get_stock_tables(database: str = "financial.db"):
    tables = []
    try:
        cursor = get_fin_db().cursor()
        sql_template = open_sql_file(get_sql_path("select_table_name_financial"))
        cursor.execute(sql_template)
        rows = cursor.fetchall()
        tables = [row[0] for row in rows]
        print(f"✅ All table names successfully fetched from database '{database}'.")
        return tables
    except Exception as e:
        print(f"❌ An error occurred while fetching tables: {e}")
        return []
