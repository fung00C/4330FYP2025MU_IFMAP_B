-- app/db/sql/select_several_stock_price.sql

SELECT /*SELECT_COLUMNS*/
FROM stock_price
WHERE 1=1
  /*SYMBOL_IN_CLAUSE*/
  /*DATE_START_COND*/
  /*DATE_END_COND*/
ORDER BY symbol, date DESC
/*DATA_LIMIT*/;
