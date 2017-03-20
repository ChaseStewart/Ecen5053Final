#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
import sys


#class Client(object):
class Hub(QtGui.QMainWindow):
    def __init__(self):
        super(Hub,self).__init__()
        self.url = "ws://52.34.209.113:8080/websocket"
        self.timeout = 5
        self.first_time=True
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.initUI()
        self.connect()
	self.my_p_callback = PeriodicCallback(self.keep_alive, 1000, io_loop=self.ioloop)
	self.my_p_callback.start()
        self.ioloop.start()
        
        
    def initUI(self):
        Disarm_btn=QtGui.QPushButton("Arm",self)
        #Disarm_btn.move(100,400)
        #Disarm_btn.setFixedSize(150,50)
        self.user_data=QtGui.QLabel(self)
        self.user_data.setText("Name")
        self.time=QtGui.QLabel(self)
        self.time.setText("Time")
        self.user_data.setFixedSize(200,50)
        self.user_data.move(0,100)
        self.time.setFixedSize(300,50)
        self.time.move(100,100)
        Disarm_btn.clicked.connect(self.sendDisarm)
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(Disarm_btn)
        hbox= QtGui.QHBoxLayout()
        hbox.addWidget(self.user_data)
        hbox.addWidget(self.time)
        grid.addLayout(hbox,0,0,1,1)
        grid.addLayout(vbox,0,1,1,1)
        wid.setLayout(grid)

        self.setGeometry(50,50,600,400)
        self.setWindowTitle('Welcome')
        self.show()
        
    def sendDisarm(self):
        if self.ws is None:
            self.connect()
        else:
            print("SEND DISARM")        
            self.ws.write_message("disarm")
        
    @gen.coroutine
    def connect(self):
        print "trying to connect"
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception, e:
            print "connection error"
        else:
            print "connected"


    def sendAndRead(self):
        print("Sending messages!")
        self.ws.write_message("login_status")
        self.readInput()
        self.ws.write_message("arm_status")
        self.readInput()

    @gen.coroutine
    def readInput(self):
        print "reading input"
        
        try:
            msg = yield self.ws.read_message()
        except:
            return

        indata = msg.split(":")
        if indata[0] == "name" :
            self.user_data.setText("Welcome, "+indata[1])
        elif indata[0] == "state" :
            self.time.setText("Arm/Disarm state is: "+indata[1])
        print indata[1]
        
    def keep_alive(self):
        if self.ws is None:
            print "reconnecting in keepalive"
            self.connect()
        else:
            #print "in keep alive"
            if self.first_time:
                self.first_time = False
            else:
                try:
                    self.ioloop.start()
                except:
                    pass
            self.sendAndRead()
            #self.timer.start(100)
            self.ioloop.stop()
            self.my_p_callback.stop()
            QTimer.singleShot(500, self.hail_mary_pass)
            

    def hail_mary_pass(self):
        self.my_p_callback.start()
        self.ioloop.start()


if __name__ == "__main__":
    #client = Client("ws://35.162.12.131:8080/websocket",5)
    app = QtGui.QApplication(sys.argv)
    hub=Hub()
    sys.exit(app.exec_())
