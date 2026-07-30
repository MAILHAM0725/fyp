# -*- coding: utf-8 -*-

# Form implementation generated for TARKEEZ Responsive Login
# Created by: Gemini (Manual Refactor using Layouts)

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TarkeezApps(object):
    def setupUi(self, TarkeezApps):
        TarkeezApps.setObjectName("TarkeezApps")
        TarkeezApps.resize(900, 600)
        TarkeezApps.setStyleSheet("background-color: #F4F2FF;")
        
        self.centralwidget = QtWidgets.QWidget(TarkeezApps)
        self.centralwidget.setObjectName("centralwidget")

        # --- Main Layout (Horizontal: Left Form | Right Image) ---
        self.mainLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(50, 50, 50, 50) # Add padding around the edges
        self.mainLayout.setSpacing(40)
        self.mainLayout.setObjectName("mainLayout")

        # =========================================================
        # LEFT SIDE: LOGIN FORM
        # =========================================================
        self.leftContainer = QtWidgets.QWidget(self.centralwidget)
        self.leftContainer.setObjectName("leftContainer")
        
        # Vertical layout for the form elements
        self.formLayout = QtWidgets.QVBoxLayout(self.leftContainer)
        self.formLayout.setAlignment(QtCore.Qt.AlignVCenter) # Center form vertically
        self.formLayout.setSpacing(15)

        # -- Title --
        self.lblTitle = QtWidgets.QLabel(self.leftContainer)
        font = QtGui.QFont()
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.lblTitle.setFont(font)
        self.lblTitle.setStyleSheet("color: #4C42D7;")
        self.lblTitle.setWordWrap(True) # Allow text to wrap if screen is small
        self.lblTitle.setText("🧠 TARKEEZ: A SMART BRAINWAVE\nMONITORING SYSTEM")
        self.lblTitle.setObjectName("lblTitle")
        self.formLayout.addWidget(self.lblTitle)

        # Spacer between title and inputs
        self.formLayout.addSpacing(20)

        # -- Email Input --
        self.lblEmail = QtWidgets.QLabel(self.leftContainer)
        self.lblEmail.setText("Email Address")
        self.lblEmail.setStyleSheet("font-weight: bold; color: #333;")
        self.formLayout.addWidget(self.lblEmail)

        self.txtEmail = QtWidgets.QLineEdit(self.leftContainer)
        self.txtEmail.setMinimumHeight(40)
        self.txtEmail.setPlaceholderText("Enter your email")
        self.txtEmail.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4C42D7;
            }
        """)
        self.formLayout.addWidget(self.txtEmail)

        # -- Password Input --
        self.lblPassword = QtWidgets.QLabel(self.leftContainer)
        self.lblPassword.setText("Password")
        self.lblPassword.setStyleSheet("font-weight: bold; color: #333;")
        self.formLayout.addWidget(self.lblPassword)

        self.txtPassword = QtWidgets.QLineEdit(self.leftContainer)
        self.txtPassword.setMinimumHeight(40)
        self.txtPassword.setPlaceholderText("Enter your password")
        self.txtPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txtPassword.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4C42D7;
            }
        """)
        self.formLayout.addWidget(self.txtPassword)

        # Spacer
        self.formLayout.addSpacing(10)

        # -- Login Button --
        self.btnLogin = QtWidgets.QPushButton(self.leftContainer)
        self.btnLogin.setMinimumHeight(45)
        self.btnLogin.setText("Login")
        self.btnLogin.setCursor(QtCore.Qt.PointingHandCursor)
        self.btnLogin.setStyleSheet("""
            QPushButton {
                background-color: #4C42D7;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5E56E0;
            }
        """)
        self.formLayout.addWidget(self.btnLogin)

        # -- Sign Up Row (Layout inside Layout) --
        self.signUpLayout = QtWidgets.QHBoxLayout()
        self.signUpLayout.setAlignment(QtCore.Qt.AlignLeft)
        
        self.label = QtWidgets.QLabel(self.leftContainer)
        self.label.setText("Don't have an account?")
        self.signUpLayout.addWidget(self.label)

        self.btnSignUp = QtWidgets.QPushButton(self.leftContainer)
        self.btnSignUp.setText("Create Account")
        self.btnSignUp.setCursor(QtCore.Qt.PointingHandCursor)
        self.btnSignUp.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4C42D7;
                border: none;
                text-decoration: underline;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #6A60E0;
            }
        """)
        self.signUpLayout.addWidget(self.btnSignUp)
        
        # Add the nested signup row to the main form
        self.formLayout.addLayout(self.signUpLayout)

        # Add Left Container to Main Layout (Stretch factor 1)
        self.mainLayout.addWidget(self.leftContainer, 1)

        # =========================================================
        # RIGHT SIDE: IMAGE
        # =========================================================
        self.rightContainer = QtWidgets.QWidget(self.centralwidget)
        self.rightContainer.setObjectName("rightContainer")
        self.rightLayout = QtWidgets.QVBoxLayout(self.rightContainer)
        self.rightLayout.setAlignment(QtCore.Qt.AlignCenter)

        self.Tarkeezimage = QtWidgets.QLabel(self.rightContainer)
        self.Tarkeezimage.setMinimumSize(250, 250)
        self.Tarkeezimage.setMaximumSize(400, 400)
        self.Tarkeezimage.setScaledContents(True)
        
        # Note: Ensure this path is correct on your new machine, or the image will be blank.
        # It's safer to use a relative path if possible.
        self.Tarkeezimage.setPixmap(QtGui.QPixmap("../Users/ASUS/OneDrive - International Islamic University Malaysia/fyp/media/TARKEEZ IMG.jpeg"))
        
        self.rightLayout.addWidget(self.Tarkeezimage)

        # Add Right Container to Main Layout (Stretch factor 1)
        self.mainLayout.addWidget(self.rightContainer, 1)


        # --- Final Setup ---
        TarkeezApps.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(TarkeezApps)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 21))
        self.menubar.setObjectName("menubar")
        TarkeezApps.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(TarkeezApps)
        self.statusbar.setObjectName("statusbar")
        TarkeezApps.setStatusBar(self.statusbar)

        self.retranslateUi(TarkeezApps)
        QtCore.QMetaObject.connectSlotsByName(TarkeezApps)

    def retranslateUi(self, TarkeezApps):
        _translate = QtCore.QCoreApplication.translate
        TarkeezApps.setWindowTitle(_translate("TarkeezApps", "TARKEEZ Login"))
        # Text is already set in the setupUi above for clarity, 
        # but you can add translation logic here if needed.

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    TarkeezApps = QtWidgets.QMainWindow()
    ui = Ui_TarkeezApps()
    ui.setupUi(TarkeezApps)
    TarkeezApps.show()
    sys.exit(app.exec_())