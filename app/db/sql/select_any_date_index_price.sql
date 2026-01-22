-- app/db/sql/select_any_date_index_price.sql

SELECT date
FROM index_price
WHERE symbol = ?
ORDER BY date DESC
LIMIT 1 OFFSET ?;