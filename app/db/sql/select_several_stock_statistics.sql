-- app/db/sql/select_several_stock_statistics.sql

SELECT /*SELECT_COLUMNS*/
FROM stock_statistics
WHERE 1=1
  /*SYMBOL_IN_CLAUSE*/
  /*TIMESTAMP_START_COND*/
  /*TIMESTAMP_END_COND*/
ORDER BY symbol, timestamp DESC
/*DATA_LIMIT*/;