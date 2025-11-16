-- app/db/sql/create_index_price_table.sql

CREATE TABLE IF NOT EXISTS index_price (
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
CREATE INDEX IF NOT EXISTS idx_index_price_symbol_date
ON index_price(symbol, date);