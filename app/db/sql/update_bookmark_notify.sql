UPDATE bookmark
SET notify = CASE 
    WHEN notify = TRUE THEN FALSE
    ELSE TRUE
END
WHERE email = ? AND stock_symbol = ?;