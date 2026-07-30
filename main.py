from PyQt5.QtCore import Qt, QCoreApplication
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

from database import DatabaseManager
db_manager = DatabaseManager()

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

# Import UI layouts
from TarkeezApps import Ui_TarkeezApps
from HomePage import Ui_HomePage
from ConnectDevice import Ui_MainWindow as Ui_ConnectDevice

# Import custom logic
from muse_manager import MuseManager
from real_time_session import RealTimeSessionWindow 
muse_manager = MuseManager()

try:
    from report_page import ReportWindow
except ImportError:
    ReportWindow = None  

import sys
from pathlib import Path
import os




# =============================================================
# HELPERS
# =============================================================
def has_csv_recursive(folder: str) -> bool:
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".csv"):
                return True
    return False


def get_base_dir() -> Path:

    base = Path.home() / "Documents" / "TARKEEZ"
    base.mkdir(parents=True, exist_ok=True)
    return base


# =============================================================
# LOGIN WINDOW
# =============================================================
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_TarkeezApps()
        self.ui.setupUi(self)

        # Connect buttons
        self.ui.btnLogin.clicked.connect(self.login_clicked)
        self.ui.btnSignUp.clicked.connect(self.signup_clicked)

        # Optional: Make password field respond to "Enter" key
        self.ui.txtPassword.returnPressed.connect(self.login_clicked)

    def login_clicked(self):
        email = self.ui.txtEmail.text().strip()
        password = self.ui.txtPassword.text().strip()

        #  Check Database
        if db_manager.authenticate_user(email, password):
            # Success
            QMessageBox.information(self, "Login", f"Welcome back, {email}!")
            self.dashboard = DashboardWindow(username=email)
            self.dashboard.show()
            self.close()
        else:
            # Failure
            QMessageBox.warning(self, "Error", "Invalid email or password.")

    def signup_clicked(self):
        # We use the text currently in the Email/Password boxes to register
        email = self.ui.txtEmail.text().strip()
        password = self.ui.txtPassword.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Sign Up", "Please enter an email and password to create an account.")
            return

        # Confirm before creating
        reply = QMessageBox.question(
            self, 
            "Create Account", 
            f"Do you want to create a new account for:\n{email}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Save to Database
            success, message = db_manager.register_user(email, password)
            
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

# =============================================================
# DASHBOARD WINDOW
# =============================================================
class DashboardWindow(QMainWindow):
    def __init__(self, username="User"):
        super().__init__()
        self.ui = Ui_HomePage()
        self.ui.setupUi(self)

        self.ui.lblGreeting.setText(f"Good Morning, {username}.")

        # Buttons
        self.ui.btnConnectDevice.clicked.connect(self.connect_device)
        self.ui.btnTraining.clicked.connect(self.training_session)
        self.ui.btnRealTime.clicked.connect(self.real_time)
        self.ui.btnReport.clicked.connect(self.report_page) 

    # -------------------------
    # Connect Device
    # -------------------------
    def connect_device(self):
        self.connect_window = ConnectDeviceWindow()
        self.connect_window.show()

    # -------------------------
    # Training Session
    # -------------------------
    def training_session(self):
        # Delayed import to avoid circular dependencies
        from training_session import TrainingSessionWindow

        self.training_window = TrainingSessionWindow(
            muse_manager=muse_manager,
            parent_window=self
        )
        self.training_window.show()
        self.hide()

    # -------------------------
    # Real-Time Session
    # -------------------------
    def real_time(self):
        # 1. Check if Muse is connected 
        if not muse_manager or not muse_manager.muse_connected:
            QMessageBox.warning(self, "Muse", "Please connect Muse first.")
            return

        # 2. Open Real-Time Window
        self.realtime_window = RealTimeSessionWindow(parent=self)
        self.realtime_window.show()
        self.hide()

    # -------------------------
    # Report Page 
    # -------------------------
    def report_page(self):
        if ReportWindow is None:
             QMessageBox.critical(self, "Error", "report_page.py was not found!")
             return

        self.report_window = ReportWindow(parent=self)
        self.report_window.show()
        self.hide()

    # -------------------------
    # Placeholders for automatic steps
    # -------------------------
    def run_preprocessing_placeholder(self):
        QMessageBox.information(
            self,
            "Info",
            "Preprocessing is now automatic after Training Session.\n"
            "No need to run it manually."
        )

    def run_ml_training_placeholder(self):
        QMessageBox.information(
            self,
            "Info",
            "Personalized ML training is now automatic after Training Session.\n"
            "Real-Time Session will use personalized model if available."
        )


# =============================================================
# CONNECT DEVICE WINDOW
# =============================================================
class ConnectDeviceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ConnectDevice()
        self.ui.setupUi(self)

        self.ui.btnConnect.clicked.connect(self.connect_muse)
        self.ui.lblStatus.setText("")

    def connect_muse(self):
        self.ui.lblStatus.setText("⚡ Connecting to Muse 2...")
        QApplication.processEvents()

        if muse_manager.connect_muse():
            self.ui.lblStatus.setText("✅ Muse connected successfully!")
        else:
            self.ui.lblStatus.setText("❌ Failed to connect.\nTry again.")


# =============================================================
#  MAIN ENTRY
# =============================================================
if __name__ == "__main__":
    print("Starting TARKEEZ...")
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())