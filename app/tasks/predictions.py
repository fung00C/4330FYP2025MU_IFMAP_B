# app/tasks/predictions.py
import numpy as np
from sklearn.preprocessing import StandardScaler
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import List

from app.utils.app_state import get_model, get_model_params

#  Create an instance of the StandardScalers for input features and output
scaler_X = StandardScaler()
scaler_y = StandardScaler()

# The Pydantic model defines the input format (e.g., a list of floating-point numbers for financial features such as stock price and trading volume).
class PredictionInput(BaseModel):
    features: List[float] = Field(..., min_items=120, max_items=120) # Adjusted to 120 inputs (60 steps x 2 features); '...' means required

# Receive input features and perform model prediction.
def predict(input_data: PredictionInput):
    # Ensure the model is loaded
    if get_model() is None:
        raise HTTPException(status_code=500, detail="Model not loaded properly")
    
    # Check if the input length meets the model requirements.
    if len(input_data.features) != get_model_params("total_inputs"):
        raise HTTPException(status_code=400, detail=f"Features must be exactly {get_model_params('total_inputs')} values for {get_model_params('timesteps')} timesteps x {get_model_params('num_features')} features")

    # Reshape the flat list to (1, 60, 2); use `astype()` to ensure the data type matches the model.
    input_array = np.array(input_data.features).reshape(1, get_model_params("timesteps"), get_model_params("num_features")).astype(np.float32)
    print(f"Input array shape: {input_array.shape}, dtype: {input_array.dtype}")
    
    # Execute prediction (adjust for your model's output, e.g., a single value or probability)
    prediction = get_model().predict(input_array, verbose=0)
    
    # Output processing (assuming a single regression output, adjust if multi-output)
    result = float(prediction[0])
    
    return {
        "input_features": input_data.features,
        "prediction": result,
        #"confidence": None  # The regression model lacks confidence.
    }

# Standardize input data
def standardize_data(closes: np.ndarray, volumes: np.ndarray):
    # Prepare X, y
    X = np.hstack([closes, volumes]) # shape (60, 2) ; hstack to horizontally stack arrays
    y = closes # shape (60, 1)

    # Standardize using StandardScaler
    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y)

    # Prepare features: [close1_scaled, volume1_scaled, close2_scaled, volume2_scaled, ..., close60_scaled, volume60_scaled]
    features = X_scaled.reshape(-1).tolist()

    # Check if enough data
    if len(features) != 120:
        print(f"⚠️ Features length {len(features)} != 120, skipping prediction")
        return
    
    return features

# Destandardize predicted data
def destandardize_data(data: np.ndarray):
    # The prediction is for the next close price, scaled. Inverse transform to get real value
    return scaler_y.inverse_transform(data)[0, 0] 