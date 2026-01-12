-- app/db/sql/create_stock_statistics_table.sql

CREATE TABLE IF NOT EXISTS stock_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    symbol TEXT NOT NULL,
    days200_start_date TEXT,
    days200_end_date TEXT,
    days200_ma REAL
);