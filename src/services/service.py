#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import serial
import json  
import pydash
from PyQt5 import QtMultimedia
from PyQt5.QtCore import QUrl, pyqtSignal, QObject
parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
root = os.path.abspath(parent)

def singleton(cls):    
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper

class Conexion:
    def __init__(self):
        # Conexión al puerto serial
        self.port = serial.Serial("/dev/ttyUSB0", baudrate=500000, timeout=1)
        # Instancia de CallModel
        self.callModel = CallModel()
        # Objeto para seleccionar los tipos de llamado
        self.types = {'a':'azul', 'n':'normal', 'b':'bano'}

    def sendMessage(self):
        dataJson = {'state': '1', 'type': 'a', 'name': '201A'}
        self.port.write('s')
        self.port.write(json.dumps(dataJson))
        self.port.write('\n')

    def listenData(self):
        # Enviando un caracter para establecer conexion bidirecional
        self.port.write('r')
        while self.port.in_waiting:
            try:
                data = json.loads(self.port.readline().rstrip('\n'))
                data['type'] = self.types[data['type']]
                self.callModel.signalUpdateCalls.emit(data)
            except:
                print('No se pudo decoficar el mensaje')

class CallService:
    def __init__(self):
        self.callModel  = CallModel()
        self.callList = []
    
    def setState(self, name, callType, state):
        if state == 1:
            self.activate(name, callType)
        else:
            self.deactivate(name)

    def activate(self, name, callType):
        index = self.callModel.roomNames.index(name)
        self.callModel.roomRows[index].activate(callType)
        self.callList.append({'name': name, 'type': callType})

    def deactivate(self, name):
        index = self.callModel.roomNames.index(name)
        self.callModel.roomRows[index].deactivate()
        pydash.remove(self.callList, {'name': name})
        if len(self.callList) > 0:
            self.callModel.callType.setIcon(self.callList[-1]['type'])
        else:
            self.callModel.callType.setIcon('None')

class Player(QtMultimedia.QMediaPlayer):
    def __init__(self):
        super(Player,self).__init__()
        azulSound = QtMultimedia.QMediaContent(QUrl.fromLocalFile(root + '/assets/azul.mp3'))
        normalSound = QtMultimedia.QMediaContent(QUrl.fromLocalFile(root + '/assets/normal.mp3'))
        banoSound = QtMultimedia.QMediaContent(QUrl.fromLocalFile(root + '/assets/bano.mp3'))
        self.typeSounds = {'azul': azulSound, 'normal': normalSound, 'bano': banoSound}
    
    def playSound(self, callType):
        self.currentSound = callType
        self.setMedia(self.typeSounds[callType])
        self.setVolume(100)
        self.play()
    
    def stopSound(self, callType):
        if self.currentSound == callType:
            self.stop()

@singleton
class CallModel(QObject):
    signalUpdateCalls = pyqtSignal(object)
    callType = None
    roomNames = []
    roomRows = []
    player = None