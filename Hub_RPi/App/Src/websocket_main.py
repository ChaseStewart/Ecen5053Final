#!/usr/bin/env python
# -*- coding: utf-8 -*-
# importing libraries required Tornado for websockets
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
import sys


# main class
class Hub(QtGui.QMainWindow):
    def __init__(self):
        super(Hub,self).__init__()
        self.url = "ws://52.34.209.113:8080/websocket" #ip of the server
        self.timeout = 1000 #timeout to connect to socket
        self.first_time=True #for error handling
        self.ioloop = IOLoop.instance() 
        self.ws = None
        self.initUI() # for Qt initialisation
        self.connect() # connect to socket
	self.my_p_callback = PeriodicCallback(self.keep_alive, self.timeout, io_loop=self.ioloop)
	self.my_p_callback.start()
        self.ioloop.start()
        
    #for PI UI setting up buttons and labels  
    def initUI(self):
        font = QtGui.QFont()
        font.setFamily(QtCore.QString.fromUtf8("FreeMono"))
        font.setBold(True)
        font.setPointSize(20)
        Disarm_btn=QtGui.QPushButton("Arm",self)
        self.user_data=QtGui.QLabel(self)
        self.user_data.setFont(font)
        self.user_data.setText("Name")
        self.state=QtGui.QLabel(self)
        self.state.setFont(font)
        self.state.setText("State")
        Disarm_btn.clicked.connect(self.sendDisarm)
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(Disarm_btn)
        hbox= QtGui.QHBoxLayout()
        hbox.addWidget(self.user_data)
        hbox.addWidget(self.state)
        grid.addLayout(hbox,0,0,1,1)
        grid.addLayout(vbox,0,1,1,1)
        wid.setLayout(grid)

        self.setGeometry(50,50,600,400)
        self.setWindowTitle('Welcome')
        self.show()
   #callback for Arm Button     
    def sendDisarm(self):
        if self.ws is None:
            self.connect()
        else:
            print("SEND DISARM")        
            self.ws.write_message("disarm")
    #to connect to server  
    @gen.coroutine
    def connect(self):
        print "trying to connect"
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception, e:
            print "connection error"
        else:
            print "connected"

    #to send data through and from websocket
    def sendAndRead(self):
        print("Sending messages!")
        self.ws.write_message("login_status")
        self.readInput()
        self.ws.write_message("arm_status")
        self.readInput()
    # to read data from websocket
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
            self.state.setText("Arm/Disarm state is: "+indata[1])
        print indata[1]
   #to keep the websocket open     
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
            self.ioloop.stop() # to unblock ioloop.start from blocking UI to
            self.my_p_callback.stop()
            QTimer.singleShot(500, self.hail_mary_pass)
    # to start ioloop.start again for websocket commmunication
    def hail_mary_pass(self):
        self.my_p_callback.start()
        self.ioloop.start()

#main
if __name__ == "__main__":
    #client = Client("ws://35.162.12.131:8080/websocket",5)
    app = QtGui.QApplication(sys.argv)
    hub=Hub()
    sys.exit(app.exec_())
