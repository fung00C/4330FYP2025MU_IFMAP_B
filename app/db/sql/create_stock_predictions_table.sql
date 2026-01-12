-- app/db/sql/create_stock_predictions_table.sql

CREATE TABLE IF NOT EXISTS stock_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    window_size INTEGER NOT NULL,
    window_start_date TEXT NOT NULL,
    window_end_date TEXT NOT NULL,
    predicted_scaled REAL NOT NULL,
    predicted_real REAL NOT NULL,
    last_actual_close REAL NOT NULL,
    recommendation TEXT NOT NULL,
    feature_number INTEGER NOT NULL,
    input_features_length INTEGER NOT NULL, 
    UNIQUE(symbol, window_start_date, window_end_date)
);