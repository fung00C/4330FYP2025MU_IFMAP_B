-- app/db/sql/insert_index_predictions_data.sql

INSERT INTO index_predictions (
    timestamp,
    window_size, 
    window_end_date,
    predicted_scaled, 
    predicted_real, 
    last_actual_close, 
    feature_number, 
    input_features_length)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);