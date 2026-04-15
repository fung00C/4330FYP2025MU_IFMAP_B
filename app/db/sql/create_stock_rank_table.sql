-- app/db/sql/create_stock_rank_table.sql

CREATE TABLE IF NOT EXISTS stock_rank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_date TEXT NOT NULL,
    symbol TEXT NOT NULL,
    sector TEXT NOT NULL,
    industry TEXT NOT NULL,
    current_price REAL NOT NULL,
    potential REAL NOT NULL,
    UNIQUE(record_date, symbol)
);

