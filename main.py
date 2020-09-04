#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
route = os.path.dirname(os.path.abspath(__file__))
sys.path.append(route + "/src/widgets")
sys.path.append(route + "/src/services")
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QStatusBar, QWidget, QGridLayout, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QDateTime, QTimer, QThread, QEvent
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

        # *********** Preferencias de Usuario *******************

        # lista para creacion de habitaciones
        self.rooms = ['201','202','203','204','205A','205B','206']
        # Puerto Serial
        portSerial = '/dev/ttyS0'
        # Duración de las alarmas
        alarmDuration = 15000 # en milisegundos

        # *********** Fin Preferencias de Usuario *******************

        # Instancia del modelo de Aplicación
        self.callModel = service.CallModel()
        self.callModel.roomNames = self.rooms
        self.callModel.portSerial = portSerial
        self.callModel.alarmDuration = alarmDuration

        # Crear todos los widgets de la interfaz
        self.createWidgets()

        # Inicializaciones
        self.flagFullScreen = False
        player = service.Player()
        self.callModel.player = player
        self.callModel.callType = self.callType
        self.callModel.roomRows = self.roomTable.roomRows
        self.callModel.signalUpdateCalls.connect(self.listenCalls)
        self.callService = service.CallService()

        # self.callService.activate('203', 'azul')

        # Timer para actualizar la hora
        self.timerHour = QTimer()
        self.timerHour.timeout.connect(self.showHour)
        self.timerHour.start(1000)

        # Iniciar conexion serial en otro hilo
        self.thread = Thread()
        self.thread.start()

        # Mostrar la interfaz
        self.showFullScreen()

    def mouseDoubleClickEvent(self, QMouseEvent):
        if (QMouseEvent.button() == Qt.LeftButton):
            if self.flagFullScreen:
                self.showFullScreen()
            else:
                self.showNormal()
            self.flagFullScreen = not self.flagFullScreen
    
    def changeEvent(self, event):
        if(event.type() == QEvent.WindowStateChange):
            if(self.isMaximized() or self.isFullScreen()):
                self.statusbar.logo.setStyleSheet('margin-right: 20px')
            else:
                self.statusbar.logo.setStyleSheet('margin-right: 0px')
        # return super(Main,self).changeEvent(event)
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

        self.statusbar = widgets.StatusBar()
        self.setStatusBar(self.statusbar)

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