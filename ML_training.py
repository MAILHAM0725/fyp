import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# ============================================================
# 1. LABEL FROM FILENAME
# ============================================================

def get_label_from_filename(filename):
    name = filename.lower()

    if "ec_post" in name:
        return "EC_Post"
    elif "eo_post" in name:
        return "EO_Post"
    elif "ec" in name:
        return "EC"
    elif "eo" in name:
        return "EO"
    elif "numstroop" in name or "num_stroop" in name:
        return "NumStroop"
    elif "stroop" in name:
        return "Stroop"

    return "Unknown"

# ============================================================
# 2. COMBINE FEATURE FILES
# ============================================================

def combine_feature_csvs(feature_folder):
    rows = []

    for file in os.listdir(feature_folder):
        if file.startswith("features_") and file.endswith(".csv"):
            path = os.path.join(feature_folder, file)

            df = pd.read_csv(path)
            df["file"] = file
            df["label"] = get_label_from_filename(file)

            rows.append(df)

            print("Loaded:", file)

    if not rows:
        raise RuntimeError("❌ No feature files found")

    return pd.concat(rows, ignore_index=True)

# ============================================================
# 3. NORMALIZATION
# ============================================================

def normalize_features(df):
    scaler = MinMaxScaler()

    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    numeric_cols = [c for c in numeric_cols if c not in ["segment"]]

    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df

# ============================================================
# 4. BUILD ML DATASET
# ============================================================

def build_ml_dataset(feature_folder, output_csv):
    print("📊 Building ML dataset...")

    df = combine_feature_csvs(feature_folder)
    df = normalize_features(df)

    df.to_csv(output_csv, index=False)
    print("✅ Saved ML dataset:", output_csv)

# ============================================================
# SAFE MAIN
# ============================================================

if __name__ == "__main__":
    from pathlib import Path

    base = Path.home() / "Documents" / "TARKEEZ"

    build_ml_dataset(
        str(base / "processed_csv"),
        str(base / "ML_dataset.csv")
    )
