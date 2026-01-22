-- app/db/sql/select_last_date_stock_predictions.sql

SELECT MAX(window_end_date) FROM stock_predictions