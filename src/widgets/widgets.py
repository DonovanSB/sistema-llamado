import sys
import os
from PyQt5.QtWidgets import QToolBar, QGraphicsDropShadowEffect, QLabel, QWidget, QSizePolicy, QFrame, QVBoxLayout, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QDateTime

class Shadow(QGraphicsDropShadowEffect):
    def __init__(self):
        super(Shadow,self).__init__()
        self.setBlurRadius(5)
        self.setXOffset(0)
        self.setYOffset(3)
        self.setColor(QColor(0,0,0,100))

class ToolBar(QToolBar):
    def __init__(self):
        super(ToolBar,self).__init__()
        self.setStyleSheet( "background-color: #0d47a1; border: 0px;" )
        self.setGraphicsEffect(Shadow())

        self.title = QLabel('Sistema de llamado')
        self.title.setStyleSheet( """margin-left: 10px;
                                font: 30px;
                                font-weight: bold;""" )
        
        self.hour = QLabel(QDateTime.currentDateTime().toString("hh:mm ap"))
        self.hour.setStyleSheet( """font: 30px;
                                margin-right: 10px;
                                font-weight: bold;""" )
        
        sizedBox = QWidget()
        sizedBox.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.addWidget(self.title)
        self.addWidget(sizedBox)
        self.addWidget(self.hour)

        self.setMovable(False)
        self.setFixedHeight(55)

class Card(QFrame):
    def __init__(self):
        super(Card,self).__init__()
        self.setStyleSheet( """ background: #9e9e9e;
                            border-radius: 10px;
                            margin: 30px 30px 30px 30px""" )
        self.setGraphicsEffect(Shadow())

        label = QLabel('Sala 1')
        self.button1 = QPushButton('1 00:01:10')
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.button1)
        

class CallType(QFrame):
    def __init__(self):
        super(CallType,self).__init__()
        self.setStyleSheet( " background: red; " )