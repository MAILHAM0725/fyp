import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, iirnotch, welch
from sklearn.preprocessing import MinMaxScaler
import os
import joblib 

# ============================================================
# CONFIG
# ============================================================

FS = 256
CHANNELS = ["TP9", "AF7", "AF8", "TP10"]

# ============================================================
# FILTERING
# ============================================================

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    return butter(order, [lowcut / nyq, highcut / nyq], btype="band")

def bandpass_filter(data, lowcut=1, highcut=45, fs=256):
    b, a = butter_bandpass(lowcut, highcut, fs)
    return filtfilt(b, a, data)

def notch_filter(data, freq=50, fs=256, Q=30):
    w0 = freq / (fs / 2)
    b, a = iirnotch(w0, Q)
    return filtfilt(b, a, data)

# ============================================================
# ARTIFACT REMOVAL
# ============================================================

def remove_artifacts(df, threshold=400):
    # Keep only rows where all channels are non-zero and within threshold
    df = df[(df[CHANNELS] != 0).all(axis=1)]
    df = df[(df[CHANNELS].abs() < threshold).all(axis=1)]
    return df.reset_index(drop=True)

# ============================================================
# SEGMENTATION
# ============================================================

def segment_data(df, window_sec=1, overlap_sec=0.5):
    win = int(window_sec * FS)
    step = int(overlap_sec * FS)

    segments = []
    start = 0

    while start + win <= len(df):
        segments.append(df.iloc[start:start + win])
        start += step

    return segments

# ============================================================
# FEATURE EXTRACTION
# ============================================================

def compute_bandpower(signal):
    # Welch's method for PSD
    f, psd = welch(signal, FS, nperseg=FS)

    def band(low, high):
        idx = (f >= low) & (f <= high)
        return np.trapz(psd[idx], f[idx])

    return {
        "delta": band(1, 4),
        "theta": band(4, 8),
        "alpha": band(8, 12),
        "beta": band(12, 30),
        "gamma": band(30, 45)
    }

# ============================================================
# LABEL FROM FILENAME
# ============================================================

def get_label_from_filename(name):
    name = name.lower()

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
# PROCESS ONE EEG CSV
# ============================================================

def preprocess_eeg(csv_path):
    print(f"[PREPROCESS] {os.path.basename(csv_path)}")

    df = pd.read_csv(csv_path)
    df = remove_artifacts(df)

    # Apply filters
    for ch in CHANNELS:
        df[ch] = bandpass_filter(df[ch])
        df[ch] = notch_filter(df[ch])

    segments = segment_data(df)

    rows = []

    for i, seg in enumerate(segments):
        row = {"segment": i + 1}
        tbr_vals = []

        for c, ch in enumerate(CHANNELS):
            bands = compute_bandpower(seg[ch].values)

            row[f"delta{c}"] = bands["delta"]
            row[f"theta{c}"] = bands["theta"]
            row[f"alpha{c}"] = bands["alpha"]
            row[f"beta{c}"] = bands["beta"]
            row[f"gamma{c}"] = bands["gamma"]

            # TBR (Theta/Beta Ratio)
            tbr = bands["theta"] / bands["beta"] if bands["beta"] != 0 else np.nan
            row[f"TBR{c}"] = tbr
            tbr_vals.append(tbr)

        row["Mean_TBR"] = np.nanmean(tbr_vals)
        rows.append(row)

    return pd.DataFrame(rows)

# ============================================================
# MAIN PIPELINE (CALLED FROM TRAINING SESSION)
# ============================================================

def build_ml_dataset_for_folder(raw_folder, output_csv):
    """
    Reads all CSVs in raw_folder, extracts features, normalizes,
    saves the Scaler, and writes the final dataset to output_csv.
    """
    all_data = []

    # 1. Process all files
    for file in os.listdir(raw_folder):
        if file.lower().endswith(".csv"):
            full_path = os.path.join(raw_folder, file)

            df_feat = preprocess_eeg(full_path)
            
            # Labeling
            df_feat["label"] = get_label_from_filename(file)
            df_feat["file"] = file

            all_data.append(df_feat)

    if not all_data:
        print("No CSV files found or processed.")
        return None

    full_df = pd.concat(all_data, ignore_index=True)

    # 2. Identify Numeric Columns for Scaling
    # We exclude 'segment', 'label', 'file' from scaling
    feature_cols = full_df.select_dtypes(include=["float64", "int64"]).columns
    feature_cols = [c for c in feature_cols if c != "segment"]

    # 3. Define and Fit Scaler
    scaler = MinMaxScaler()
    full_df[feature_cols] = scaler.fit_transform(full_df[feature_cols])

    # We save it in the same folder as the output CSV, or a fixed location
    scaler_path = os.path.join(os.path.dirname(output_csv), "tarkeez_scaler.joblib")
    joblib.dump(scaler, scaler_path)
    print(f"[PREPROCESS] Scaler saved to: {scaler_path}")

    # 5. Save Final Dataset
    full_df.to_csv(output_csv, index=False)
    print("[PREPROCESS] ML dataset created:", output_csv)
    
    return output_csv