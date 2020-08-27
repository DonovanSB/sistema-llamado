import sys
import os
route = os.path.dirname(os.path.abspath(__file__))
sys.path.append(route + "/src/widgets")
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QFrame, QPushButton, QMainWindow, QToolBar, QLabel, QGraphicsDropShadowEffect, QWidget, QSizePolicy, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QDateTime, QTimer
import widgets

class Main(QMainWindow):
    def __init__(self):
        super(Main,self).__init__()
         #--- Variables Ventana------
        self.sizeWindow = QDesktopWidget().availableGeometry()
        self.width = 900
        self.height = 550

        self.setWindowTitle("Sistema de llamado")
        self.setGeometry(0,0,self.width,self.height)
        self.centerWindow()

        self.createWidgets()

        self.timerHour = QTimer()
        self.timerHour.setInterval(1000)
        self.timerHour.timeout.connect(self.showHour)
        self.timerHour.start()

        self.show()

    def showHour(self):
        self.toolbar.hour.setText(QDateTime.currentDateTime().toString("hh:mm ap"))

    def centerWindow(self):
        S_Screen = QDesktopWidget().availableGeometry().center()
        S_Win = self.geometry()
        self.move(S_Screen.x()-S_Win.width()/2,S_Screen.y() - S_Win.height()/2)

    def createWidgets(self):
        self.toolbar = widgets.ToolBar()
        self.addToolBar(self.toolbar)

        self.card = widgets.Card()
        self.callType = widgets.CallType()

        widgetGrid = QWidget()
        grid = QGridLayout(widgetGrid)
        grid.addWidget(self.callType,0,0)
        grid.addWidget(self.card,0,1,1,2)
        grid.setContentsMargins(0,0,0,0)
        self.setCentralWidget(widgetGrid)
        
        
if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Main()
    sys.exit(App.exec_())