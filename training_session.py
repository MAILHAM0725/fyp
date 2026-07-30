import os
import time
import threading
import csv
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QMessageBox, QSizePolicy, QApplication
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView

from pylsl import StreamInlet, resolve_byprop

# ✅ IMPORT THE NEW GAMES
try:
    from Stroop_Game import run_stroop_game
    from NumStroop_Game import run_num_stroop_game
except ImportError:
    print("⚠️ PsychoPy games not found or PsychoPy not installed!")

class TrainingSessionWindow(QMainWindow):
    def __init__(self, muse_manager=None, parent_window=None):
        super().__init__()

        # ================= PASSED FROM main.py =================
        self.muse_manager = muse_manager
        self.parent_window = parent_window

        self.setWindowTitle("TARKEEZ - Training Session")
        self.setGeometry(200, 100, 1200, 800)

        # ================= FOLDERS =================
        base_dir = Path.home() / "Documents" / "TARKEEZ" / "raw_csv"
        base_dir.mkdir(parents=True, exist_ok=True)

        # Create unique session folder with timestamp
        session_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_folder = base_dir / f"session_{session_time}"
        self.session_folder.mkdir(exist_ok=True)

        print(f"[TRAINING SESSION] Saving to: {self.session_folder}")

        # ================= UI SETUP =================
        self.central = QWidget(self)
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)

        # Header
        header = QHBoxLayout()
        self.btnBack = QPushButton("⬅ Back")
        self.btnBack.clicked.connect(self.go_back)

        self.lblTitle = QLabel("🧠 TARKEEZ Training Session")
        self.lblTitle.setAlignment(Qt.AlignCenter)
        self.lblTitle.setStyleSheet("font-size:26px;font-weight:bold;color:#4C42D7;")

        header.addWidget(self.btnBack)
        header.addStretch()
        header.addWidget(self.lblTitle)
        header.addStretch()
        self.layout.addLayout(header)

        # Instructions & Timer
        self.lblInstruction = QLabel("Click Start to begin training.")
        self.lblInstruction.setAlignment(Qt.AlignCenter)
        self.lblInstruction.setStyleSheet("font-size:18px;")

        self.lblTimer = QLabel("00:00")
        self.lblTimer.setAlignment(Qt.AlignCenter)
        self.lblTimer.setStyleSheet("font-size:30px;font-weight:bold; color: #e74c3c;")

        self.media_display = QLabel()
        self.media_display.setAlignment(Qt.AlignCenter)
        self.media_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.webview = QWebEngineView()
        self.webview.hide()

        self.btnStart = QPushButton("Start Training")
        self.btnStart.clicked.connect(self.start_training)

        self.btnSkip = QPushButton("⏭ Skip Phase")
        self.btnSkip.clicked.connect(self.skip_phase)

        self.layout.addWidget(self.lblInstruction)
        self.layout.addWidget(self.media_display, 1)
        self.layout.addWidget(self.webview, 1)
        self.layout.addWidget(self.lblTimer)
        self.layout.addWidget(self.btnStart)
        self.layout.addWidget(self.btnSkip)

        # ================= VARIABLES =================
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.phase_index = 0
        self.seconds_left = 0
        self.is_training = False

        self.eeg_inlet = None
        self.recording = False
        self.record_thread = None
        self.phase_rows = []

        # ================= PHASES =================
        self.phases = [
            ("EC", "media/Eye_Closed.jpg"),
            ("EO", "media/Eye_Opened.jpg"),
            ("Stroop", "GAME"),
            ("NumStroop", "GAME"),
            ("EC_Post", "media/Eye_Closed.jpg"),
            ("EO_Post", "media/Eye_Opened.jpg"),
        ]
        
        # Duration for each phase (seconds)
        self.durations = [60, 60, 120, 120, 60, 60]

    def setup_eeg_stream(self):
        if self.eeg_inlet: return
        streams = resolve_byprop("type", "EEG", timeout=5)
        if not streams: raise RuntimeError("No EEG stream found")
        self.eeg_inlet = StreamInlet(streams[0])

    def record_loop(self):
        while self.recording:
            try:
                sample, ts = self.eeg_inlet.pull_sample(timeout=1.0)
                if sample:
                    self.phase_rows.append([ts] + sample[:4])
            except: pass

    def start_recording(self):
        try:
            self.setup_eeg_stream()
            self.phase_rows = []
            self.recording = True
            self.record_thread = threading.Thread(target=self.record_loop, daemon=True)
            self.record_thread.start()
        except Exception as e:
            QMessageBox.critical(self, "EEG Error", f"Stream error: {e}")

    def stop_and_save(self, phase_name):
        self.recording = False
        if self.record_thread:
            self.record_thread.join(timeout=1)
        
        file_path = self.session_folder / f"{phase_name}.csv"
        try:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "TP9", "AF7", "AF8", "TP10"])
                writer.writerows(self.phase_rows)
            print(f"[EEG SAVED] {file_path}")
        except Exception as e:
            print(f"Error saving CSV: {e}")

    # =======================================================
    # TRAINING LOGIC
    # =======================================================
    def start_training(self):
        if not self.muse_manager or not self.muse_manager.muse_connected:
            QMessageBox.warning(self, "Muse", "Please connect Muse first.")
            return

        self.is_training = True
        self.phase_index = 0
        self.btnStart.setEnabled(False)
        self.next_phase()

    def next_phase(self):
        if self.phase_index >= len(self.phases):
            QMessageBox.information(self, "Done", "Training Finished! Processing...")
            self.run_post_training_pipeline()
            return

        phase_name, media_path = self.phases[self.phase_index]
        duration = self.durations[self.phase_index]
        
        self.lblInstruction.setText(f"Phase {self.phase_index + 1}: {phase_name}")
        self.seconds_left = duration
        self.lblTimer.setText(f"{duration // 60:02d}:{duration % 60:02d}")
        
        # 1. Start EEG Recording
        self.start_recording()

        # 2. Check if Game
        if media_path == "GAME":
            # We start the timer in the background so it counts down
            self.timer.start(1000)
            self.handle_game_phase(phase_name, duration)
        else:
            self.handle_media_phase(media_path)
            self.timer.start(1000)

    def handle_game_phase(self, phase_name, duration):
        """
        Runs PsychoPy game in windowed mode.
        """
        self.media_display.hide()
        self.webview.hide()
        self.lblInstruction.setText(f"PLAYING {phase_name}... Look at the game window!")
        
        QApplication.processEvents()

        game_result_path = self.session_folder / f"{phase_name}_Results.csv"

        try:
            if phase_name == "Stroop":
                run_stroop_game(duration, str(game_result_path))
            elif phase_name == "NumStroop":
                run_num_stroop_game(duration, str(game_result_path))
        except Exception as e:
            print(f"Game Error: {e}")
            QMessageBox.warning(self, "Error", f"Could not run game: {e}")

        # When game loop finishes (duration ends), we stop everything
        self.stop_and_save(phase_name)
        self.timer.stop()
        self.phase_index += 1
        self.next_phase()

    def handle_media_phase(self, media):
        """
        Handles Image display only. 
        If image is not found, it keeps the previous screen or shows blank.
        """
        self.webview.hide()
        self.media_display.show()
        
        pix = QPixmap(media)
        if not pix.isNull():
            self.media_display.setPixmap(pix.scaled(
                self.media_display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self.media_display.setText(f"Please Focus: {media}")

    def skip_phase(self):
        self.timer.stop()
        phase_name = self.phases[self.phase_index][0]
        self.stop_and_save(phase_name)
        self.phase_index += 1
        self.next_phase()

    def update_timer(self):
        if self.seconds_left > 0:
            self.lblTimer.setText(f"{self.seconds_left // 60:02d}:{self.seconds_left % 60:02d}")
            self.seconds_left -= 1
        else:
            if self.phases[self.phase_index][1] != "GAME":
                self.skip_phase()

    def run_post_training_pipeline(self):
        try:
            from preprocessing_Complete import build_ml_dataset_for_folder
            from XGBoost_TARKEEZ import train_personalized_model

            # =========================================================================
            # CHANGED: Create a timestamped filename for the dataset
            # This ensures we know exactly which session this data belongs to.
            # =========================================================================
            
            # Using the session folder name (which already has a timestamp)
            session_name = self.session_folder.name  # e.g., "session_2026-01-03_14-05-12"
            
            # New dataset name: "Dataset_session_2026-01-03_14-05-12.csv"
            dataset_filename = f"Dataset_{session_name}.csv"
            
            # Save it alongside the raw session folder or in a common datasets folder
            # Here we save it inside the session folder itself for easy finding:
            root_dataset_path = str(self.session_folder / dataset_filename)

            # We also update the model path to be specific if you want, 
            # or keep it global to update the "current best" model. 
            # For now, we keep the model global so the live session can find it easily.
            root_model_path = "tarkeez_personalized_model.joblib"

            print(f"[PIPELINE] Processing data from: {self.session_folder}")
            print(f"[PIPELINE] Saving dataset to: {root_dataset_path}")
            
            dataset_path = build_ml_dataset_for_folder(
                raw_folder=str(self.session_folder),
                output_csv=root_dataset_path
            )

            train_personalized_model(
                dataset_path=dataset_path,
                model_output=root_model_path
            )

            QMessageBox.information(
                self,
                "Model Ready",
                f"Training Complete! 🧠\n\n"
                f"Dataset Saved as:\n{dataset_filename}\n\n"
                "Your Personal AI Model has been updated."
            )
            
            self.go_back()

        except Exception as e:
            print(f"Pipeline Error: {e}")
            QMessageBox.critical(self, "Pipeline Error", f"Error:\n{str(e)}")

    def go_back(self):
        self.timer.stop()
        self.hide()
        if self.parent_window:
            self.parent_window.show()