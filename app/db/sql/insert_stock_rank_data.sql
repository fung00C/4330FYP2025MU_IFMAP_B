-- app/db/sql/insert_stock_rank_data.sql

INSERT INTO stock_rank (
    timestamp,
    symbol,
    record_date,
    sector,
    industry,
    current_price,
    potential)
VALUES (?, ?, ?, ?, ?, ?, ?);