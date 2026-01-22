-- app/db/sql/insert_stock_predictions_data.sql

INSERT INTO stock_predictions (
    symbol,
    timestamp,
    window_size, 
    window_start_date,
    window_end_date,
    predicted_scaled, 
    predicted_real, 
    last_actual_close, 
    recommendation, 
    feature_number, 
    input_features_length)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);