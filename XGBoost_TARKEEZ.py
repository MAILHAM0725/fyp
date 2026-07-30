import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# ============================================================
# TRAIN PERSONALIZED MODEL
# ============================================================

def train_personalized_model(dataset_path, model_output):
    print("[ML] Loading dataset:", dataset_path)

    df = pd.read_csv(dataset_path)

    # 1. Clean labels
    df["label"] = df["label"].astype(str).str.strip().str.upper()

    # Define your "Mental States"
    # 0 = Relaxed / Baseline
    # 1 = Recovery (Post)
    # 2 = High Focus (Stroop)
    label_map = {
        "EO": 0, "EC": 0,
        "EO_POST": 1, "EC_POST": 1,
        "STROOP": 2, "NUMSTROOP": 2
    }

    df["attention_label"] = df["label"].map(label_map)
    df = df.dropna(subset=["attention_label"])
    df["attention_label"] = df["attention_label"].astype(int)

    # 2. DROP NON-FEATURE COLUMNS
    # WARNING: 'segment' is a number, so select_dtypes would include it! 
    # We must explicitly drop it to prevent the model from cheating.
    ignore_cols = ["label", "segment", "file", "attention_label"]
    
    # Select features (Numeric columns that are NOT in ignore_cols)
    feature_cols = [c for c in df.columns if c not in ignore_cols and np.issubdtype(df[c].dtype, np.number)]
    
    X = df[feature_cols]
    y = df["attention_label"]
    
    print(f"[ML] Training on {len(X)} samples with features: {list(X.columns)}")

    # 3. Handle very small datasets safely
    test_size = 0.2 if len(df) > 50 else 0.3

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    # 4. Configure Model
    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob", # Returns probabilities for each class
        num_class=3,                # 0, 1, 2
        eval_metric="mlogloss"
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"[ML] Personalized model accuracy: {acc:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, model_output)
    print("[ML] Model saved:", model_output)

    return model_output