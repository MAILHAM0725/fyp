# -*- coding: utf-8 -*-

# Form implementation generated for TARKEEZ Responsive Home Page
# Created by: Gemini (Manual Refactor using Layouts)

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HomePage(object):
    def setupUi(self, HomePage):
        HomePage.setObjectName("HomePage")
        HomePage.resize(1000, 700)  # Increased default size for better visibility
        HomePage.setStyleSheet("background-color: #FFFFFF;")
        
        # --- Central Widget ---
        self.centralwidget = QtWidgets.QWidget(HomePage)
        self.centralwidget.setObjectName("centralwidget")
        
        # --- Main Horizontal Layout (Left Sidebar | Center Content | Right Sidebar) ---
        self.mainLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)  # No margins on edges
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName("mainLayout")

        # ---------------------------------------------------------
        # 1. LEFT SIDEBAR
        # ---------------------------------------------------------
        self.leftSidebar = QtWidgets.QFrame(self.centralwidget)
        self.leftSidebar.setFixedWidth(80)  # Fixed width so it acts like a sidebar
        self.leftSidebar.setStyleSheet("background-color: #4C42D7; border: none;")
        self.leftSidebar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.leftSidebar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.leftSidebar.setObjectName("leftSidebar")
        
        # Left Sidebar Layout (To hold the tool button at the top)
        self.leftLayout = QtWidgets.QVBoxLayout(self.leftSidebar)
        self.leftLayout.setContentsMargins(0, 40, 0, 0) # Top margin 40
        self.leftLayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        
        self.toolButton = QtWidgets.QToolButton(self.leftSidebar)
        self.toolButton.setMinimumSize(QtCore.QSize(41, 31))
        self.toolButton.setStyleSheet("background-color: rgba(255,255,255,0.2); border-radius: 5px; color: white;")
        self.toolButton.setObjectName("toolButton")
        self.leftLayout.addWidget(self.toolButton)
        
        self.mainLayout.addWidget(self.leftSidebar)

        # ---------------------------------------------------------
        # 2. CENTER CONTENT (Greeting + Buttons)
        # ---------------------------------------------------------
        # We use a container widget for the center area
        self.centerContentWidget = QtWidgets.QWidget(self.centralwidget)
        self.centerContentWidget.setObjectName("centerContentWidget")
        
        # Vertical Layout to center items vertically
        self.centerLayout = QtWidgets.QVBoxLayout(self.centerContentWidget)
        self.centerLayout.setSpacing(20)
        self.centerLayout.setAlignment(QtCore.Qt.AlignCenter)  # Center everything inside
        
        # -- Spacer to push content to middle --
        spacerItemTop = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.centerLayout.addItem(spacerItemTop)

        # -- Greeting Label --
        self.lblGreeting = QtWidgets.QLabel(self.centerContentWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblGreeting.setFont(font)
        self.lblGreeting.setStyleSheet("""
            background-color: #F4F2FF;
            color: #4C42D7;
            border-radius: 20px;
            padding: 15px 30px;
        """)
        self.lblGreeting.setAlignment(QtCore.Qt.AlignCenter)
        self.lblGreeting.setObjectName("lblGreeting")
        self.centerLayout.addWidget(self.lblGreeting)

        # -- Buttons Container --
        # Define the Button Style
        btn_style = """
        QPushButton {
            border: 2px solid #4C42D7;
            border-radius: 10px;
            color: #333333;
            font-size: 14px;
            padding: 12px;
            background-color: #FFFFFF;
            min-width: 250px;
        }
        QPushButton:hover {
            background-color: #F4F2FF;
            cursor: pointer;
        }
        """
        
        self.btnConnectDevice = QtWidgets.QPushButton(self.centerContentWidget)
        self.btnConnectDevice.setStyleSheet(btn_style)
        self.btnConnectDevice.setObjectName("btnConnectDevice")
        self.centerLayout.addWidget(self.btnConnectDevice)

        self.btnTraining = QtWidgets.QPushButton(self.centerContentWidget)
        self.btnTraining.setStyleSheet(btn_style)
        self.btnTraining.setObjectName("btnTraining")
        self.centerLayout.addWidget(self.btnTraining)

        self.btnRealTime = QtWidgets.QPushButton(self.centerContentWidget)
        self.btnRealTime.setStyleSheet(btn_style)
        self.btnRealTime.setObjectName("btnRealTime")
        self.centerLayout.addWidget(self.btnRealTime)

        self.btnReport = QtWidgets.QPushButton(self.centerContentWidget)
        self.btnReport.setStyleSheet(btn_style)
        self.btnReport.setObjectName("btnReport")
        self.centerLayout.addWidget(self.btnReport)

        # -- Spacer to push content to middle (bottom side) --
        spacerItemBottom = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.centerLayout.addItem(spacerItemBottom)

        # Add Center Widget to Main Layout
        self.mainLayout.addWidget(self.centerContentWidget)

        # ---------------------------------------------------------
        # 3. RIGHT SIDEBAR
        # ---------------------------------------------------------
        self.rightSidebar = QtWidgets.QFrame(self.centralwidget)
        self.rightSidebar.setFixedWidth(160) # Fixed width
        self.rightSidebar.setStyleSheet("background-color: #4C42D7;")
        self.rightSidebar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.rightSidebar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.rightSidebar.setObjectName("rightSidebar")
        
        self.mainLayout.addWidget(self.rightSidebar)

        # --- Finalize ---
        HomePage.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(HomePage)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 21))
        self.menubar.setObjectName("menubar")
        HomePage.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(HomePage)
        self.statusbar.setObjectName("statusbar")
        HomePage.setStatusBar(self.statusbar)

        self.retranslateUi(HomePage)
        QtCore.QMetaObject.connectSlotsByName(HomePage)

    def retranslateUi(self, HomePage):
        _translate = QtCore.QCoreApplication.translate
        HomePage.setWindowTitle(_translate("HomePage", "TARKEEZ Dashboard"))
        self.toolButton.setText(_translate("HomePage", "..."))
        self.lblGreeting.setText(_translate("HomePage", "Good Morning, User."))
        self.btnConnectDevice.setText(_translate("HomePage", "Connect Device"))
        self.btnTraining.setText(_translate("HomePage", "Training Session"))
        self.btnRealTime.setText(_translate("HomePage", "Real-Time Session"))
        self.btnReport.setText(_translate("HomePage", "Report"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    HomePage = QtWidgets.QMainWindow()
    ui = Ui_HomePage()
    ui.setupUi(HomePage)
    HomePage.show()
    sys.exit(app.exec_())