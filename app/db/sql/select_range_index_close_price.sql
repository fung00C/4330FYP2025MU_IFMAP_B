-- app/db/sql/select_range_index_close_price.sql

SELECT close
FROM index_price
WHERE symbol = ?
ORDER BY date DESC
LIMIT ?;