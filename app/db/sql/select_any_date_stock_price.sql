-- app/db/sql/select_any_date_stock_price.sql

SELECT date
FROM stock_price
WHERE symbol = ?
ORDER BY date DESC
LIMIT 1 OFFSET ?;