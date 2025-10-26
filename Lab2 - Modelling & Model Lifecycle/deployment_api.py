from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Load the trained model and metadata
model_artifact = joblib.load("saved_models/best_ridge_model.joblib")
model = model_artifact['model']
feature_names = model_artifact['feature_names']

# FastAPI app
app = FastAPI(title="Ridge Model API with Metrics")

# Pydantic model for input validation
class PredictionRequest(BaseModel):
    features: dict             # Example: {"feature1": 0.5, "feature2": 1.2, ...}
    true_value: float = None   # Optional: for monitoring metrics if available

# In-memory logs for monitoring
prediction_log = []

# Helper function to convert input dict to dataframe
def dict_to_df(input_dict):
    df = pd.DataFrame([input_dict])
    df = df.reindex(columns=feature_names, fill_value=0)
    return df

@app.post("/predict")
def predict(request: PredictionRequest):
    X_new = dict_to_df(request.features)
    pred = model.predict(X_new)[0]

    # Initialize metrics
    rmse, mae, r2 = None, None, None

    # Compute metrics if true value is provided
    if request.true_value is not None:
        y_true = np.array([request.true_value])
        y_pred = np.array([pred])
        rmse = mean_squared_error(y_true, y_pred, squared=False)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

    # Log prediction and metrics
    log_entry = {
        'timestamp': datetime.utcnow(),
        'input': request.features,
        'prediction': float(pred),
        'true_value': request.true_value,
        'rmse': rmse,
        'mae': mae,
        'r2': r2
    }
    prediction_log.append(log_entry)

    return {
        "prediction": float(pred),
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
        "message": "Prediction successful"
    }

@app.get("/metrics")
def get_metrics():
    """
    Aggregate metrics across all logged predictions.
    """
    if not prediction_log:
        return {"message": "No predictions yet."}

    # Filter entries with true_value
    logged_metrics = [entry for entry in prediction_log if entry['true_value'] is not None]
    if not logged_metrics:
        return {"message": "No true values provided yet. Cannot compute performance metrics."}

    y_true = np.array([entry['true_value'] for entry in logged_metrics])
    y_pred = np.array([entry['prediction'] for entry in logged_metrics])

    return {
        "total_predictions": len(prediction_log),
        "logged_metrics_count": len(logged_metrics),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred))
    }

# To run the API, use:
# uvicorn deployment_api:app --reload