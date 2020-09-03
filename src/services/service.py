#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import serial
import json  
import pydash
from vlc import MediaPlayer, Media
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
        # Instancia de CallModel
        self.callModel = CallModel()
        # Conexión al puerto serial
        self.port = serial.Serial(self.callModel.portSerial, baudrate=500000, timeout=1)
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
            self.deactivate(name, callType)

    def activate(self, name, callType):
        index = self.callModel.roomNames.index(name)
        
        # Verificando si hay un llamado anterior con codigo azul o Baño
        checkAzul = pydash.find(self.callList,{'name': name, 'type': 'azul'})
        checkBano = pydash.find(self.callList,{'name': name, 'type': 'bano'})

        # Si hay un llamado con codigo azul no se activará el entrante
        if (checkAzul and self.callModel.roomRows[index].isActive):
            return
        # Si hay un llamado de baño y el entrante es un llamado normal, no se activará el entrante
        if (checkBano and self.callModel.roomRows[index].isActive and callType=='normal'):
            return

        self.callModel.roomRows[index].activate(callType)
        self.callList.append({'name': name, 'type': callType})

    def deactivate(self, name, callType):
        index = self.callModel.roomNames.index(name)
        self.callModel.roomRows[index].deactivate(callType)
        pydash.remove(self.callList, {'name': name})
        if len(self.callList) > 0:
            self.callModel.callType.setIcon(self.callList[-1]['type'])
        else:
            self.callModel.callType.setIcon('None')


class Player:
    def __init__(self):
        self.player = MediaPlayer()
        azulSound = Media(root + '/assets/azul.mp3')
        normalSound = Media(root + '/assets/normal.mp3')
        banoSound = Media(root + '/assets/bano.mp3')
        self.typeSounds = {'azul': azulSound, 'normal': normalSound, 'bano': banoSound}
        self.currentSound = None

    def playSound(self, callType):
        self.currentSound = callType
        self.player.set_media(self.typeSounds[callType])
        self.player.audio_set_volume(100)
        self.player.play()
    
    def stopSound(self, callType):
        if self.currentSound == callType:
            if self.player.is_playing():
                self.player.stop()

@singleton
class CallModel(QObject):
    signalUpdateCalls = pyqtSignal(object)
    callType = None
    roomNames = []
    roomRows = []
    player = None
    portSerial = None
    alarmDuration = None