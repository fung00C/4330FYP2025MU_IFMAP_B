-- app/db/sql/create_stock_price_table.sql

CREATE TABLE IF NOT EXISTS stock_price (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    UNIQUE(symbol, date)
);
CREATE INDEX IF NOT EXISTS idx_stock_price_symbol_date
ON stock_price(symbol, date);
