# Steel Plant Production Prediction

This project focuses on predicting crude steel production using various plant-level features. The solution includes data exploration, model training with hyperparameter optimization using Optuna, and a FastAPI-based deployment with monitoring capabilities.

## Project Structure

```
.
├── README.md
├── plant_production_predictions.ipynb                      # Main Jupyter notebook with EDA and modeling
├── deployment_api.py                                       # FastAPI application for model serving
├── saved_models/                                           # Directory containing trained models
│   └── best_ridge_model.joblib                             # Serialized model and metadata
├── mlflow_runs/                                            # MLflow experiment tracking
├── Plant-level-data-Global-Iron-and-Steel-Tracker.xlsx     # Raw data
└── crude_steel_plants_dataset.csv                          # Processed dataset
```

## Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If requirements.txt doesn't exist, install the following packages:*
   ```bash
   pip install pandas numpy scikit-learn optuna mlflow fastapi uvicorn python-multipart pydantic joblib
   ```

## Data

The dataset contains information about steel plants worldwide, including:
- Plant characteristics (capacity, workforce size, etc.)
- Production metrics
- Geographic and operational details

## Notebook Overview (`plant_production_predictions.ipynb`)

The Jupyter notebook includes:

1. **Data Loading and Exploration**
   - Loading and merging datasets
   - Handling missing values
   - Exploratory Data Analysis (EDA)

2. **Data Preprocessing**
   - Feature engineering
   - Handling categorical variables
   - Train-test split

3. **Model Training**
   - Ridge regression with hyperparameter tuning using Optuna
   - Cross-validation
   - Performance metrics (MSE, RMSE, MAE, R²)

4. **Model Evaluation**
   - Feature importance analysis
   - Performance visualization
   - Model persistence

## API Deployment (`deployment_api.py`)

A FastAPI application that serves the trained model with the following endpoints:

### Endpoints

- `POST /predict`
  - Input: JSON with features and optional true value
  - Output: Prediction and metrics (if true value provided)
  
  Example request:
  ```json
  {
    "features": {
      "Start date": 2000,
      "Workforce size": 500,
      "Nominal crude steel capacity (ttpa)": 2000
    },
    "true_value": 2100
  }
  ```

- `GET /metrics`
  - Returns aggregate performance metrics across all predictions
  - Only includes predictions where true values were provided

### Running the API

```bash
uvicorn deployment_api:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### API Documentation

Once the API is running, access the interactive documentation at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Model Monitoring

The API includes basic monitoring capabilities:
- Logs all predictions with timestamps
- Tracks prediction metrics when true values are provided
- Provides aggregate statistics via the `/metrics` endpoint