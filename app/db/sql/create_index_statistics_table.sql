-- app/db/sql/create_index_statistics_table.sql

CREATE TABLE IF NOT EXISTS index_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ticker TEXT NOT NULL,
    days200_start_date TEXT,
    days200_end_date TEXT,
    days200_ma REAL
);