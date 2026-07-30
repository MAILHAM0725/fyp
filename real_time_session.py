# real_time_session.py

import sys
import time
import numpy as np
import pandas as pd
import joblib
import os
from collections import deque
from datetime import datetime
from pathlib import Path
from scipy.signal import welch

# ✅ IMPORT WINSOUND FOR ALERTS (Windows Only)
try:
    import winsound
except ImportError:
    winsound = None

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

import pyqtgraph as pg
from pylsl import StreamInlet, resolve_byprop

# ============================================================
# CONFIG
# ============================================================
FS = 256
CHANNELS = ["TP9", "AF7", "AF8", "TP10"]
SCALER_FILE = "tarkeez_scaler.joblib"

MODEL_GLOBAL = "tarkeez_xgb_model.joblib"
MODEL_PERSONAL = "tarkeez_personalized_model.joblib"

# ============================================================
# EEG WORKER THREAD
# ============================================================

class EEGWorker(QThread):
    # Signals: Focus Score (%), Confidence (%), Timestamp
    update_ui = pyqtSignal(float, float, float)
    
    def __init__(self, model, trained_cols):
        super().__init__()
        self.model = model
        self.trained_cols = trained_cols
        self.running = True
        self.scaler = None
        
        # Load scaler
        if os.path.exists(SCALER_FILE):
            try:
                self.scaler = joblib.load(SCALER_FILE)
                print(f"✅ [RealTime] Scaler loaded: {SCALER_FILE}")
            except Exception as e:
                print(f"❌ [RealTime] Error loading scaler: {e}")
        else:
            print(f"⚠️ [RealTime] Warning: {SCALER_FILE} not found.")

    def calculate_features(self, buffer_np):
        row = {}
        tbr_vals = []
        
        for c, ch_name in enumerate(CHANNELS):
            signal = buffer_np[:, c]
            f, psd = welch(signal, FS, nperseg=FS)

            def band_power(low, high):
                idx = (f >= low) & (f <= high)
                return np.trapz(psd[idx], f[idx])

            b_delta = band_power(1, 4)
            b_theta = band_power(4, 8)
            b_alpha = band_power(8, 12)
            b_beta  = band_power(12, 30)
            b_gamma = band_power(30, 45)

            row[f"delta{c}"] = b_delta
            row[f"theta{c}"] = b_theta
            row[f"alpha{c}"] = b_alpha
            row[f"beta{c}"]  = b_beta
            row[f"gamma{c}"] = b_gamma

            tbr = b_theta / b_beta if b_beta != 0 else 0
            row[f"TBR{c}"] = tbr
            tbr_vals.append(tbr)

        row["Mean_TBR"] = np.nanmean(tbr_vals)
        return row

    def run(self):
        print("🔍 [RealTime] Resolving EEG stream...")
        streams = resolve_byprop("type", "EEG", timeout=5)

        if not streams:
            print("❌ [RealTime] No EEG stream found. Check Muse / LSL.")
            return

        inlet = StreamInlet(streams[0])
        buffer_len = FS * 1  
        buffer = deque(maxlen=buffer_len)

        print("✅ [RealTime] Stream started. Collecting data...")

        while self.running:
            try:
                sample, timestamp = inlet.pull_sample(timeout=1.0)
                if not sample: 
                    continue
                    
                buffer.append(sample[:4])

                if len(buffer) == buffer_len:
                    data_np = np.array(buffer)
                    feat_dict = self.calculate_features(data_np)
                    feat_df = pd.DataFrame([feat_dict])
                    
                    try:
                        feat_df = feat_df[self.trained_cols]
                    except KeyError:
                        feat_df = feat_df.reindex(columns=self.trained_cols, fill_value=0)

                    if self.scaler:
                        X_input = self.scaler.transform(feat_df)
                    else:
                        X_input = feat_df.values

                    probs = self.model.predict_proba(X_input)[0]
                    focus_prob = probs[2]  # Class 2 = Focus
                    confidence = max(probs) * 100
                    focus_score = focus_prob * 100

                    self.update_ui.emit(focus_score, confidence, timestamp)
            except Exception as e:
                print(f"Stream Error: {e}")
                time.sleep(0.1)

# ============================================================
# REAL TIME WINDOW
# ============================================================

class RealTimeSessionWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("TARKEEZ - Real Time Focus")
        self.resize(800, 600)
        self.parent_window = parent

        # ==========================================
        # 📂 [NEW] PREPARE SAVE FOLDER FOR REPORTS
        # ==========================================
        self.save_dir = Path.home() / "Documents" / "TARKEEZ" / "live_sessions"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.session_data_log = []  # Store data here

        # --------------------------------------------------------
        # 1. MODEL SELECTION
        # --------------------------------------------------------
        self.model = None
        self.trained_cols = []
        self.current_mode = "Unknown"

        if os.path.exists(MODEL_PERSONAL):
            self.load_model(MODEL_PERSONAL)
            self.current_mode = "Personalized 👤"
            self.mode_color = "#2ecc71" # Green
        elif os.path.exists(MODEL_GLOBAL):
            self.load_model(MODEL_GLOBAL)
            self.current_mode = "Global 🌐"
            self.mode_color = "#3498db" # Blue
        else:
            QMessageBox.critical(self, "Error", "No Models Found!\nPlease run Training Session first.")
            self.close()
            return

        # --------------------------------------------------------
        # 2. ALERT & TIMER VARIABLES
        # --------------------------------------------------------
        self.last_alert_time = 0
        self.alert_cooldown = 15      # Seconds to wait between popups
        
        self.low_focus_start_time = None  
        self.LOW_FOCUS_DURATION_THRESHOLD = 2.0  # Must be low for 5 seconds

        self.popup_dialog = None  

        # --------------------------------------------------------
        # 3. UI SETUP
        # --------------------------------------------------------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.lblModelStatus = QLabel(f"Using Model: {self.current_mode}")
        self.lblModelStatus.setAlignment(Qt.AlignCenter)
        self.lblModelStatus.setStyleSheet(f"background-color: {self.mode_color}; color: white; padding: 5px; font-weight: bold; border-radius: 5px;")
        self.lblModelStatus.setFixedHeight(30)
        layout.addWidget(self.lblModelStatus)

        self.lblFocus = QLabel("Focus: -- %")
        self.lblFocus.setFont(QFont("Arial", 24, QFont.Bold))
        self.lblFocus.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lblFocus)

        self.lblLevel = QLabel("Level: --")
        self.lblLevel.setFont(QFont("Arial", 16))
        self.lblLevel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lblLevel)

        self.lblConfidence = QLabel("Confidence: -- %")
        self.lblConfidence.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lblConfidence)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("Real-Time Focus Score")
        self.plot_widget.setYRange(0, 100)
        self.curve = self.plot_widget.plot(pen='y')
        layout.addWidget(self.plot_widget)

        # Stop Button
        self.btnStop = QPushButton("Stop & Save Session")
        self.btnStop.clicked.connect(self.stop_session) # [UPDATED] Calls save logic
        layout.addWidget(self.btnStop)

        self.focus_buf = []

        self.worker = EEGWorker(self.model, self.trained_cols)
        self.worker.update_ui.connect(self.update_display)
        self.worker.start()

    def load_model(self, path):
        print(f"✅ Loading Model: {path}")
        self.model = joblib.load(path)
        try:
            self.trained_cols = self.model.get_booster().feature_names
        except:
            self.trained_cols = [f"delta{i}" for i in range(4)] + \
                                [f"theta{i}" for i in range(4)] + \
                                [f"alpha{i}" for i in range(4)] + \
                                [f"beta{i}" for i in range(4)] + \
                                [f"gamma{i}" for i in range(4)] + \
                                [f"TBR{i}" for i in range(4)] + ["Mean_TBR"]

    def update_display(self, focus, confidence, timestamp):
        # 1. Update UI Text
        self.lblFocus.setText(f"Focus: {focus:.1f} %")
        self.lblConfidence.setText(f"Confidence: {confidence:.1f} %")

        # ==========================
        # ⚠️ ALERT LOGIC (Sound + Popup)
        # ==========================
        if focus < 30:
            level, color = "LOW (Distracted)", "red"
            
            if self.low_focus_start_time is None:
                self.low_focus_start_time = time.time()
            
            # Check duration (Low for > 5s)
            duration_low = time.time() - self.low_focus_start_time
            if duration_low >= self.LOW_FOCUS_DURATION_THRESHOLD:
                self.check_for_alert()
                
        else:
            level = "MEDIUM (Neutral)" if focus < 70 else "HIGH (Focused)"
            color = "orange" if focus < 70 else "green"
            self.low_focus_start_time = None

        self.lblLevel.setText(f"Level: {level}")
        self.lblLevel.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18px;")

        # 2. Update Plot
        self.focus_buf.append(focus)
        if len(self.focus_buf) > 100:
            self.focus_buf.pop(0)
        self.curve.setData(self.focus_buf)

        # ==========================
        # 💾 [NEW] LOG DATA FOR SAVING
        # ==========================
        current_dt = datetime.now()
        self.session_data_log.append({
            "timestamp": current_dt,
            "hour": current_dt.hour,  # For Morning/Evening analysis
            "focus_score": focus,
            "confidence": confidence
        })

    def check_for_alert(self):
        current_time = time.time()
        # Check cooldown
        if current_time - self.last_alert_time > self.alert_cooldown:
            self.trigger_popup()
            self.last_alert_time = current_time

    def trigger_popup(self):
        # 🔊 SOUND
        if winsound:
            winsound.MessageBeep(winsound.MB_ICONHAND)
        else:
            QApplication.beep()

        # 💬 POPUP
        self.popup_dialog = QMessageBox(self)
        self.popup_dialog.setIcon(QMessageBox.Warning)
        self.popup_dialog.setWindowTitle("⚠️ Focus Alert")
        self.popup_dialog.setText("Attention has been low for 5 seconds!")
        self.popup_dialog.setInformativeText("Take a deep breath and try to refocus.")
        self.popup_dialog.setStandardButtons(QMessageBox.Ok)
        self.popup_dialog.setWindowModality(Qt.NonModal)
        self.popup_dialog.show()
        self.popup_dialog.raise_()
        self.popup_dialog.activateWindow()

    # ==========================================
    # 🛑 STOP AND SAVE FUNCTION
    # ==========================================
    def stop_session(self):
        # 1. Stop Worker
        if hasattr(self, 'worker'):
            self.worker.running = False
            self.worker.quit()
            self.worker.wait()

        # 2. Save CSV if data exists
        if self.session_data_log:
            try:
                df = pd.DataFrame(self.session_data_log)
                filename = f"live_session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
                save_path = self.save_dir / filename
                
                df.to_csv(save_path, index=False)
                print(f"✅ Session saved to: {save_path}")
                
                QMessageBox.information(
                    self, 
                    "Session Saved", 
                    f"Session complete!\nData saved for Report analysis."
                )
            except Exception as e:
                print(f"Error saving CSV: {e}")

        self.close()

    def closeEvent(self, event):
        self.stop_session()
        if self.parent_window:
            self.parent_window.show()
        event.accept()