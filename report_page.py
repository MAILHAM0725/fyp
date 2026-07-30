# report_page.py

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QListWidget, 
    QSplitter, QFrame, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import pyqtgraph as pg

# Folders
TRAINING_DIR = Path.home() / "Documents" / "TARKEEZ" / "raw_csv"
LIVE_DIR = Path.home() / "Documents" / "TARKEEZ" / "live_sessions"

class ReportWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("TARKEEZ - Analytics Dashboard")
        self.resize(1100, 750)
        self.parent_window = parent

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)

        # Header
        header = QHBoxLayout()
        self.btnBack = QPushButton("⬅ Back")
        self.btnBack.clicked.connect(self.go_back)
        lblTitle = QLabel("Performance & Rhythm Analytics")
        lblTitle.setStyleSheet("font-size: 24px; font-weight: bold; color: #4C42D7;")
        header.addWidget(self.btnBack)
        header.addStretch()
        header.addWidget(lblTitle)
        header.addStretch()
        self.layout.addLayout(header)

        # TABS
        self.tabs = QTabWidget()
        
        # Tab 1: Training Progress (Existing)
        self.tab_training = QWidget()
        self.setup_training_tab()
        
        # Tab 2: Live Insights (NEW!)
        self.tab_live = QWidget()
        self.setup_live_tab()

        self.tabs.addTab(self.tab_live, "Daily Rhythm (Live Sessions)")
        self.tabs.addTab(self.tab_training, "Training History")
        
        self.layout.addWidget(self.tabs)
        
        # Load Data
        self.load_live_data()

    # =======================================================
    # TAB 1: TRAINING (Simplified version of previous code)
    # =======================================================
    def setup_training_tab(self):
        layout = QVBoxLayout(self.tab_training)
        # (You can paste your previous training graph logic here)
        layout.addWidget(QLabel("Training History Graphs go here..."))

    # =======================================================
    # TAB 2: LIVE RHYTHM (The New Feature)
    # =======================================================
    def setup_live_tab(self):
        layout = QVBoxLayout(self.tab_live)

        # Insight Text
        self.lblInsight = QLabel("Gathering data...")
        self.lblInsight.setAlignment(Qt.AlignCenter)
        self.lblInsight.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; padding: 20px;")
        self.lblInsight.setWordWrap(True)
        layout.addWidget(self.lblInsight)

        # Bar Chart for Time of Day
        self.plot_rhythm = pg.PlotWidget(title="Average Focus by Time of Day")
        self.plot_rhythm.setLabel('left', 'Avg Focus Score', units='%')
        self.plot_rhythm.setLabel('bottom', 'Time Period')
        layout.addWidget(self.plot_rhythm)

    def load_live_data(self):
        if not LIVE_DIR.exists():
            self.lblInsight.setText("No live sessions found yet. Go do some work!")
            return

        all_files = list(LIVE_DIR.glob("*.csv"))
        if not all_files:
            self.lblInsight.setText("No live session data recorded.")
            return

        # Combine all live sessions into one big DataFrame
        df_list = []
        for f in all_files:
            try:
                df = pd.read_csv(f)
                df_list.append(df)
            except: pass
        
        if not df_list: return
        
        full_df = pd.concat(df_list)

        # ANALYZE TIME OF DAY
        # Morning: 5 AM - 12 PM
        # Afternoon: 12 PM - 6 PM (18:00)
        # Evening: 6 PM - 4 AM
        
        morning = full_df[(full_df['hour'] >= 5) & (full_df['hour'] < 12)]
        afternoon = full_df[(full_df['hour'] >= 12) & (full_df['hour'] < 18)]
        evening = full_df[(full_df['hour'] >= 18) | (full_df['hour'] < 5)]

        avg_m = morning['focus_score'].mean() if not morning.empty else 0
        avg_a = afternoon['focus_score'].mean() if not afternoon.empty else 0
        avg_e = evening['focus_score'].mean() if not evening.empty else 0

        # Update Chart
        # X-axis: 1=Morning, 2=Afternoon, 3=Evening
        bg1 = pg.BarGraphItem(x=[1], height=[avg_m], width=0.6, brush='#f1c40f', name="Morning")
        bg2 = pg.BarGraphItem(x=[2], height=[avg_a], width=0.6, brush='#e67e22', name="Afternoon")
        bg3 = pg.BarGraphItem(x=[3], height=[avg_e], width=0.6, brush='#8e44ad', name="Evening")
        
        self.plot_rhythm.clear()
        self.plot_rhythm.addItem(bg1)
        self.plot_rhythm.addItem(bg2)
        self.plot_rhythm.addItem(bg3)
        
        # Custom Axis Labels
        ax = self.plot_rhythm.getAxis('bottom')
        ax.setTicks([[(1, 'Morning\n(5am-12pm)'), (2, 'Afternoon\n(12pm-6pm)'), (3, 'Evening\n(6pm-4am)')]])

        # GENERATE INSIGHT TEXT
        scores = {"Morning": avg_m, "Afternoon": avg_a, "Evening": avg_e}
        best_time = max(scores, key=scores.get)
        best_score = scores[best_time]

        if best_score == 0:
            insight = "Not enough data yet."
        else:
            insight = (
                f"💡 ANALYSIS: You are a {best_time} person!\n\n"
                f"Your brain shows the highest focus ({best_score:.1f}%) during the {best_time.split()[0]}.\n"
                "Recommendation: Schedule your hardest tasks for this time."
            )
        
        self.lblInsight.setText(insight)

    def go_back(self):
        self.close()
        if self.parent_window:
            self.parent_window.show()

# Test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ReportWindow()
    win.show()
    sys.exit(app.exec_())