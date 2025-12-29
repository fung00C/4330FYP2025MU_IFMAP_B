# app/tasks/model.py
import tensorflow as tf

from app.utils.app_state import set_model, set_model_params

def load_model():
    # Load the Keras .h5 model
    try:
        model = tf.keras.models.load_model('../backend/models/pre_sp500_model2.h5')
        print("✅ ML model loaded successfully.")
        set_model(model)
    except Exception as e:
        print(f"❌ Error loading ML model: {e}")
        model = None

    # Check the input shape (feature count is shape[-1], exclude batches).
    input_shape = model.input_shape
    print("Input shape:", input_shape)

    # Time step
    timesteps = input_shape[1]  # 60
    print("Time step:", timesteps)

    # Number of features
    num_features = input_shape[2]  # 2
    print("Number of features:", num_features)

    # Total input length (time step * number of features)
    total_inputs = timesteps * num_features  # 120
    print("Total input length:", total_inputs)

    # Check data type
    data_type = model.inputs[0].dtype
    print("Input data type:", data_type)

    # Print model summary for visualization
    model.summary()

    # Set model parameters in app state
    set_model_params(timesteps, num_features, total_inputs)
