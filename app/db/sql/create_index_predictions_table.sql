-- app/db/sql/create_index_predictions_table.sql

CREATE TABLE IF NOT EXISTS index_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    predicted_scaled REAL NOT NULL,
    predicted_real REAL NOT NULL,
    last_actual_close REAL NOT NULL,
    input_features_length INTEGER NOT NULL
);