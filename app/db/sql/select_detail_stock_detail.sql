-- app/db/sql/select_detail_stock_detail.sql

SELECT Exchange, ShortName, LongName, Sector, Industry, MarketCap, Ebitda, RevenueGrowth, City, State, Country, FullTimeEmployees, LongBusinessSummary
FROM stock_detail
WHERE symbol = ?