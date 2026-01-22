-- app/db/sql/insert_stock_statistics_data.sql

INSERT INTO stock_statistics (
    symbol,
    timestamp,
    days200_start_date,
    days200_end_date,
    days200_ma)
VALUES (?, ?, ?, ?, ?);