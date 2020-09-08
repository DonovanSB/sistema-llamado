#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import datetime
from PyQt5.QtWidgets import QToolBar, QGraphicsDropShadowEffect, QLabel, QStatusBar, QWidget, QSizePolicy, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtCore import Qt, QDateTime, QTimer, QThread, QElapsedTimer
parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
root = os.path.abspath(parent)
sys.path.append(root + "/src/services")
import service

class Shadow(QGraphicsDropShadowEffect):
    def __init__(self):
        super(Shadow,self).__init__()
        self.setBlurRadius(10)
        self.setXOffset(0)
        self.setYOffset(4)
        self.setColor(QColor(0,0,0,150))

class ToolBar(QToolBar):
    def __init__(self):
        super(ToolBar,self).__init__()
        self.setStyleSheet( "background-color: #0d47a1; border: 0px;" )
        self.setGraphicsEffect(Shadow())

        self.title = QLabel('Sistema de llamado')
        self.title.setStyleSheet( """margin-left: 10px;
                                font: 30px;
                                font-weight: bold;
                                color: white """ )
        
        self.hour = QLabel(QDateTime.currentDateTime().toString("hh:mm ap"))
        self.hour.setStyleSheet( "margin-right: 10px; color: white" )

        self.hour.setFont(QFont('DS-Digital', 35, QFont.Bold))
        
        sizedBox = QWidget()
        sizedBox.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.addWidget(self.title)
        self.addWidget(sizedBox)
        self.addWidget(self.hour)

        self.setMovable(False)
        self.setFixedHeight(55)
        self.setContextMenuPolicy(Qt.PreventContextMenu)

class RoomTable(QFrame):
    def __init__(self, rooms):
        super(RoomTable,self).__init__()
        self.rooms = rooms
        self.setStyleSheet( """QFrame {background: #9e9e9e;
                            border-radius: 10px;
                            margin: 30px 30px 10px 30px}""" )
        self.setGraphicsEffect(Shadow())

        header1 = self.createHeaders()
        header2 = self.createHeaders()

        self.roomRows = []
        for room in self.rooms:
            self.roomRows.append(RoomRow(room))

        grid = QGridLayout(self)
        grid.setAlignment(Qt.AlignTop)
        grid.addWidget(header1, 0,0)
        grid.addWidget(header2, 0,1)
        numRooms = len(self.rooms)
        for i in range((numRooms+1)/2):
            grid.addWidget(self.roomRows[2*i],i+1,0)
            if 2*i+1 < numRooms:
                grid.addWidget(self.roomRows[2*i+1],i+1,1)
    
    def createHeaders(self):
        headers = RoomRow('Habitación')
        headers.setFixedHeight(60)
        headers.setStyleSheet("QFrame {background: transparent; margin: 0px}")

        headers.room.setStyleSheet('font: 20px; color: white; font-weight: bold')
        headers.timePassed.setText('Tiempo\n Transcurrido')
        headers.timePassed.setStyleSheet('font: 20px; color: white; font-weight: bold')
        headers.timePassed.setFont(QFont())
        return headers


class RoomRow(QFrame):
    def __init__(self, idRoom):
        super(RoomRow,self).__init__()
        self.setStyleSheet( 'QFrame {background: #757575; border-radius: 10px; margin: 0px}' )
        self.setFixedHeight(50)

        self.callModel = service.CallModel()

        self.elapsedTimer = QElapsedTimer()
        self.elapsedTimer.start()
        self.timerSingle = QTimer()
        self.timerSingle.setSingleShot(True)
        self.timerSingle.timeout.connect(self.deactivateBlink)

        self.timer = QTimer()
        self.timer.timeout.connect(self.blink)
        self.stopwatch = QTimer()
        self.stopwatch.timeout.connect(self.updateStopwatch)

        self.types = {'azul': '#0d47a1', 'normal': '#00e676', 'bano': '#fdd835'}
        self.flagBlink = True
        self.isActive = False
        self.callType = None

        self.room = QLabel(idRoom)
        self.room.setStyleSheet('font: 25px; color: white')
        self.room.setAlignment(Qt.AlignCenter)
        self.timePassed = QLabel('—')
        self.timePassed.setStyleSheet('color: white')
        self.timePassed.setFont(QFont('DS-Digital', 25))
        self.timePassed.setAlignment(Qt.AlignCenter)
        
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.room)
        hbox.addWidget(self.timePassed)

    def activate(self, callType):
        self.isActive = True
        self.callType = callType

        self.callModel.callType.setIcon(callType)
        self.elapsedTimer.restart()
        self.timer.start(500)
        self.stopwatch.start(1000)
        self.callModel.player.playSound(callType)
        
        self.timerSingle.start(self.callModel.alarmDuration)

    def deactivate(self, callType):
        self.isActive = False
        self.stopwatch.stop()
        self.timer.stop()
        self.timerSingle.stop()
        self.disable()
        self.timePassed.setText('—')
        self.callModel.player.stopSound(callType)

    def deactivateBlink(self):
        self.timer.stop()
        if self.isActive:
            self.enable()
            if (self.callType != 'azul'):
                self.callModel.player.stopSound(self.callType)

    def updateStopwatch(self):
        self.timePassed.setText(str(datetime.timedelta(seconds=self.elapsedTimer.elapsed()/1000)))

    def blink(self):
        if self.flagBlink:
            self.enable()
        else:
            self.disable()
        self.flagBlink = not self.flagBlink

    def enable(self, callType = None):
        if callType:
            self.setStyleSheet( 'QFrame {background:' + self.types[callType] + '; border-radius: 10px; margin: 0px}' )
        else:
            self.setStyleSheet( 'QFrame {background:' + self.types[self.callType] + '; border-radius: 10px; margin: 0px}' )

    def disable(self):
        self.setStyleSheet( 'QFrame {background: #757575; border-radius: 10px; margin: 0px}' )
    

class CallType(QFrame):
    def __init__(self):
        super(CallType,self).__init__()
        self.setStyleSheet( "QFrame {border: 0px; border-right : 1px solid black}" )
        self.types = {'azul': 'Codigo Azul', 'normal': 'Llamado', 'bano': 'Baño'}

        self.logoH = QLabel()
        self.logoH.setAlignment(Qt.AlignCenter)
        self.logoH.setStyleSheet(' border: 0px; margin-bottom: 10px')
        pixmapLogoH = QPixmap(root + '/assets/logohospital.png')
        self.logoH.setPixmap(pixmapLogoH)

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setStyleSheet(' border: 0px; margin: 0px')

        self.textType = QLabel()
        self.textType.setStyleSheet('color: white; font: 35px; font-weight: bold; border: 0px')
        self.textType.setAlignment(Qt.AlignCenter)

        frameTypes = QFrame()
        frameTypes.setStyleSheet('border: 0px')
        vboxTypes = QVBoxLayout(frameTypes)
        vboxTypes.setAlignment(Qt.AlignCenter)
        vboxTypes.addWidget(self.icon)
        vboxTypes.addWidget(self.textType)

        vbox = QVBoxLayout(self)
        vbox.setAlignment(Qt.AlignTop)
        vbox.addWidget(self.logoH)
        vbox.addWidget(frameTypes, 1)
        

    def setIcon(self, callType):
        if callType == 'None':
            self.icon.setText(' ')
            self.textType.setText('')
        else:
            pixmapIcon = QPixmap(root + '/assets/' + callType + '.svg')
            self.icon.setPixmap(pixmapIcon)
            self.textType.setText(self.types[callType])   

class StatusBar(QStatusBar):
    def __init__(self):
        super(StatusBar,self).__init__()
        self.setStyleSheet('QStatusBar::item {border: None;}')
        self.logo = QLabel()
        self.logo.setStyleSheet('margin-right: 0px')
        image = QPixmap(root + '/assets/logoempresa.png')
        self.logo.setPixmap(image)
        self.addPermanentWidget(self.logo)


