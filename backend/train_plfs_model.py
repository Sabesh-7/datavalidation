import os
import zipfile
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

ZIP_PATH = r"E:\Data in CSV.zip"
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

os.makedirs(MODEL_DIR, exist_ok=True)

def train_plfs_model():
    print(f"Loading real PLFS dataset from {ZIP_PATH} ...")
    
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(f"ZIP file not found at {ZIP_PATH}")

    with zipfile.ZipFile(ZIP_PATH) as z:
        print("Reading Person Level data (cperv1.csv) ...")
        # Load sample for high performance training
        df_per = pd.read_csv(z.open("cperv1.csv"), nrows=50000, low_memory=False)
        
        print("Reading Household Level data (chhv1.csv) ...")
        df_hh = pd.read_csv(z.open("chhv1.csv"), nrows=50000, low_memory=False)

    print(f"Loaded {len(df_per)} Person records and {len(df_hh)} Household records.")

    # Select numerical features for multivariate ML anomaly training
    per_features = ["Age", "Years_Formal_Education", "Principal_Status_Code", "CWS_Earnings_Salaried", "CWS_Earnings_SelfEmployed"]
    hh_features = ["Household_Size", "Usual_Expenditure", "Monthly_Consumer_Expenditure"]

    # Preprocessing Person dataset
    df_p = df_per[per_features].copy()
    for col in per_features:
        df_p[col] = pd.to_numeric(df_p[col], errors='coerce').fillna(0)

    # Preprocessing Household dataset
    df_h = df_hh[hh_features].copy()
    for col in hh_features:
        df_h[col] = pd.to_numeric(df_h[col], errors='coerce').fillna(0)

    # Combine statistical features
    X_train = df_p.values

    # Train StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    # Train Isolation Forest Model for Multivariate Outlier / Anomaly Detection
    print("Training Isolation Forest ML model on PLFS dataset...")
    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=0.05,  # Expected 5% anomaly rate
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_scaled)

    # Save model and scaler artifacts
    model_path = os.path.join(MODEL_DIR, "plfs_isolation_forest.joblib")
    scaler_path = os.path.join(MODEL_DIR, "plfs_scaler.joblib")
    joblib.dump(iso_forest, model_path)
    joblib.dump(scaler, scaler_path)

    # Compute baseline statistical metrics from real PLFS dataset
    stats_metadata = {
        "dataset_name": "MoSPI Periodic Labour Force Survey (PLFS)",
        "zip_source": ZIP_PATH,
        "person_records_sampled": len(df_per),
        "household_records_sampled": len(df_hh),
        "features_used": per_features,
        "mean_age": float(df_p["Age"].mean()),
        "std_age": float(df_p["Age"].std()),
        "mean_education_years": float(df_p["Years_Formal_Education"].mean()),
        "mean_monthly_expenditure": float(df_h["Monthly_Consumer_Expenditure"].mean()),
        "max_monthly_expenditure": float(df_h["Monthly_Consumer_Expenditure"].max()),
        "model_type": "Unsupervised Isolation Forest Anomaly Estimator",
        "contamination_rate": 0.05,
        "status": "TRAINED_AND_SAVED"
    }

    metadata_path = os.path.join(MODEL_DIR, "plfs_model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(stats_metadata, f, indent=2)

    print(f"SUCCESS: Model trained and saved to {model_path}")
    print(f"Metadata saved to {metadata_path}")
    return stats_metadata

if __name__ == "__main__":
    train_plfs_model()
