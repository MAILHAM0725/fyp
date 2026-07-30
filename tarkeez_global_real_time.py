import os
import time
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from pylsl import StreamInlet, resolve_byprop

# ============================================================
# 1. MODEL SELECTION (PERSONALIZED → GLOBAL FALLBACK)
# ============================================================

BASE_DIR = Path.home() / "Documents" / "TARKEEZ"

PERSONAL_MODEL_PATH = BASE_DIR / "latest_personalized_model.joblib"
GLOBAL_MODEL_PATH = BASE_DIR / "global_model" / "tarkeez_xgb_model.joblib"


def load_tarkeez_model():
    if PERSONAL_MODEL_PATH.exists():
        print("✅ Using PERSONALIZED model")
        return joblib.load(PERSONAL_MODEL_PATH), "PERSONALIZED"
    else:
        print("⚠️ Personalized model not found → using GLOBAL model")
        return joblib.load(GLOBAL_MODEL_PATH), "GLOBAL"


print("Loading TARKEEZ model...")
model, MODEL_TYPE = load_tarkeez_model()
print(f"Model loaded: {MODEL_TYPE}")

# ============================================================
# 2. FEATURE METADATA
# ============================================================

if hasattr(model, "get_booster"):
    trained_cols = list(model.get_booster().feature_names)
elif hasattr(model, "feature_names_in_"):
    trained_cols = list(model.feature_names_in_)
else:
    raise RuntimeError("Model does not contain feature metadata")

print(f"Expected features: {len(trained_cols)}")

# ============================================================
# 3. CONNECT TO MUSE EEG STREAM
# ============================================================

print("Resolving Muse EEG stream...")
streams = resolve_byprop("type", "EEG", timeout=10)

if not streams:
    raise RuntimeError("No EEG stream found. Please start Muse / muselsl.")

inlet = StreamInlet(streams[0], max_chunklen=12)
info = inlet.info()

fs = int(info.nominal_srate())
USE_CHANNELS = 4

print(f"Connected to {info.name()} | fs={fs} Hz")

# ============================================================
# 4. WINDOW SETTINGS
# ============================================================

WIN_SEC = 2
WIN_SIZE = int(WIN_SEC * fs)

buffer = np.zeros((WIN_SIZE, USE_CHANNELS), dtype=np.float32)
filled = 0

# ============================================================
# 5. SESSION TYPE (MATCH TRAINING)
# ============================================================

SESSION = "Stroop"   # EC / EO / EC_Post / EO_Post / Stroop / NumStroop
SESSIONS = ["EC", "EO", "EC_Post", "EO_Post", "Stroop", "NumStroop"]

def encode_session(name):
    return {f"session_type_{s}": int(s == name) for s in SESSIONS}

# ============================================================
# 6. BANDPOWER EXTRACTION
# ============================================================

def compute_bandpowers(data, fs):
    n = data.shape[0]
    freqs = np.fft.rfftfreq(n, 1 / fs)
    fft_vals = np.fft.rfft(data, axis=0)
    psd = (np.abs(fft_vals) ** 2) / n

    bands = {
        "delta": (1, 4),
        "theta": (4, 8),
        "alpha": (8, 13),
        "beta":  (13, 30),
        "gamma": (30, 45),
    }

    out = {}
    for band, (low, high) in bands.items():
        idx = (freqs >= low) & (freqs <= high)
        out[band] = psd[idx].sum(axis=0)

    return out

# ============================================================
# 7. LABEL MAP
# ============================================================

LABEL_MAP = {
    0: "🔴 LOW",
    1: "🟡 MEDIUM",
    2: "🟢 HIGH"
}

# ============================================================
# 8. REAL-TIME LOOP
# ============================================================

print("\n🧠 TARKEEZ Real-Time Session Started (Ctrl+C to stop)\n")

try:
    while True:
        chunk, timestamps = inlet.pull_chunk(timeout=1.0, max_samples=WIN_SIZE)

        if timestamps:
            chunk = np.array(chunk, dtype=np.float32)[:, :USE_CHANNELS]
            n_new = chunk.shape[0]

            if n_new >= WIN_SIZE:
                buffer[:] = chunk[-WIN_SIZE:]
                filled = WIN_SIZE
            else:
                buffer = np.roll(buffer, -n_new, axis=0)
                buffer[-n_new:] = chunk
                filled = min(WIN_SIZE, filled + n_new)

            if filled == WIN_SIZE:
                bands = compute_bandpowers(buffer, fs)

                sample = {}
                for ch in range(USE_CHANNELS):
                    sample[f"delta{ch}"] = bands["delta"][ch]
                    sample[f"theta{ch}"] = bands["theta"][ch]
                    sample[f"alpha{ch}"] = bands["alpha"][ch]
                    sample[f"beta{ch}"]  = bands["beta"][ch]
                    sample[f"gamma{ch}"] = bands["gamma"][ch]

                for ch in range(USE_CHANNELS):
                    beta = sample[f"beta{ch}"]
                    theta = sample[f"theta{ch}"]
                    sample[f"TBR{ch}"] = theta / beta if beta > 0 else 0.0

                sample.update(encode_session(SESSION))

                df = pd.DataFrame([sample])
                df = df.reindex(columns=trained_cols, fill_value=0)

                pred = int(model.predict(df)[0])
                proba = model.predict_proba(df)[0]

                confidence = np.max(proba) * 100
                focus_score = proba[0]*0 + proba[1]*50 + proba[2]*100

                print(
                    f"[{MODEL_TYPE}] "
                    f"Focus={focus_score:6.1f}% | "
                    f"{LABEL_MAP[pred]} | "
                    f"Conf={confidence:5.1f}%"
                )

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nTARKEEZ real-time session stopped 👋")
