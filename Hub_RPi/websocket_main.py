#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from PyQt4 import QtGui, QtCore
import sys


#class Client(object):
class Hub(QtGui.QMainWindow):
    def __init__(self):
        super(Hub,self).__init__()
        self.url = "ws://52.34.209.113:8080/websocket"
        self.timeout = 5
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.initUI()
        self.connect()
	self.my_p_callback = PeriodicCallback(self.keep_alive, 20000, io_loop=self.ioloop)
	self.my_p_callback.start()
        self.ioloop.start()
        
    def initUI(self):
        Disarm_btn=QtGui.QPushButton("Disarm",self)
        Disarm_btn.move(100,400)
        Disarm_btn.setFixedSize(150,50)
        self.user_data=QtGui.QLabel(self)
        self.user_data.setFixedSize(200,50)
        self.user_data.move(0,100)
        Disarm_btn.clicked.connect(self.sendDisarm)
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
            self.ws.write_message("login_status")
            self.ws.write_message("arm_status")
            self.run()

    @gen.coroutine
    def run(self):
        print "run"
        msg = yield self.ws.read_message()
        self.user_data.setText(msg)
        print msg
        
    def keep_alive(self):
        if not self.my_p_callback.is_running():
            self.ioloop.start()
        if self.ws is None:
            self.connect()
        else:
            self.run()
        self.ioloop.stop()


if __name__ == "__main__":
    #client = Client("ws://35.162.12.131:8080/websocket",5)
    app = QtGui.QApplication(sys.argv)
    hub=Hub()
    sys.exit(app.exec_())
