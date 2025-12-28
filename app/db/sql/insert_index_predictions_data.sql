-- app/db/sql/insert_index_predictions_data.sql

INSERT INTO index_predictions (
    predicted_scaled, 
    predicted_real, 
    last_actual_close, 
    input_features_length)
VALUES (?, ?, ?, ?);