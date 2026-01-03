-- app/db/sql/insert_index_statistics_data.sql

INSERT INTO index_statistics (
    ticker,
    timestamp,
    days200_start_date,
    days200_end_date,
    days200_ma)
VALUES (?, ?, ?, ?, ?);