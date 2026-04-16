SELECT stock_symbol
FROM bookmark
WHERE email = ? AND notify = TRUE;