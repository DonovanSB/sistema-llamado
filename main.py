import sys
import os
import time
route = os.path.dirname(os.path.abspath(__file__))
sys.path.append(route + "/src/widgets")
sys.path.append(route + "/src/services")
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QDateTime, QTimer, QThread
import widgets
import service

class Main(QMainWindow):
    def __init__(self):
        super(Main,self).__init__()
         #--- Variables Ventana------
        self.sizeWindow = QDesktopWidget().availableGeometry()
        self.width = 900
        self.height = 550

        # Agregar titulo a la app
        self.setWindowTitle("Sistema de llamado")
        self.setGeometry(0,0,self.width,self.height)

        # Cambiar estilo de la ventana principal
        self.setStyleSheet('QMainWindow {background: #424242}')
        # Funcion para centrar la ventana
        self.centerWindow()

        # lista para creacion de habitaciones
        self.rooms = ['201','202','203','204','205 A','205 B']
        
        # Instancia del modelo de Aplicación
        self.callModel = service.CallModel()
        self.callModel.roomNames = self.rooms

        # Crear todos los widgets de la interfaz
        self.createWidgets()

        # Inicializaciones
        player = service.Player()
        self.callModel.player = player
        self.callModel.callType = self.callType
        self.callModel.roomRows = self.roomTable.roomRows
        self.callModel.signalUpdateCalls.connect(self.listenCalls)
        self.callService = service.CallService()

        # Timer para actualizar la hora
        self.timerHour = QTimer()
        self.timerHour.timeout.connect(self.showHour)
        self.timerHour.start(1000)

        # Iniciar conexion serial en otro hilo
        self.thread = Thread()
        self.thread.start()

        # Mostrar la interfaz
        self.show()

    def closeEvent(self, event):
        self.reply = QMessageBox.question(None,' ',"¿Realmente desea cerrar la aplicación?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if self.reply == QMessageBox.Yes:
            self.thread.stop()
            event.accept()
        else:
            event.ignore()

    # Función usada para actualizar la hora
    def showHour(self):
        self.toolbar.hour.setText(QDateTime.currentDateTime().toString("hh:mm ap"))

    def centerWindow(self):
        S_Screen = QDesktopWidget().availableGeometry().center()
        S_Win = self.geometry()
        self.move(S_Screen.x()-S_Win.width()/2,S_Screen.y() - S_Win.height()/2)

    def createWidgets(self):

        self.callType = widgets.CallType()
        self.roomTable = widgets.RoomTable(self.rooms)

        widgetGrid = QWidget()
        grid = QGridLayout(widgetGrid)
        grid.addWidget(self.callType,0,0)
        grid.addWidget(self.roomTable,0,1,1,3)
        grid.setContentsMargins(0,0,0,0)
        self.setCentralWidget(widgetGrid)
        
        self.toolbar = widgets.ToolBar()
        self.addToolBar(self.toolbar)
    
    def listenCalls(self, data):
        self.callService.setState(data['name'], data['type'], data['state'])


# Clase para un nuevo hilo
class Thread(QThread):

    def __init__(self):
        super(Thread,self).__init__()
        self.threadactive = True
        # Establecer conexión con el puerto serial
        self.conexion = service.Conexion()

    def run(self):
        while self.threadactive:
            # ciclo para estar pendiente de mensajes
            self.conexion.listenData()
            time.sleep(0.3)
    
    def stop(self):
        self.threadactive = False

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Main()
    sys.exit(App.exec_())