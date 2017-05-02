#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys, json, numpy
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from helpers import WindowState



class LEDWindow(QtGui.QMainWindow):
    """
    This is the window that should be shown when the device is locked
    """

    def __init__(self, parent=None):
        """
        initialize this window
        """
	super(LEDWindow, self).__init__(parent)
        self.initUI()
        self.parent = parent


    def initUI(self):

	# create QT font
        self.font = QtGui.QFont()
        self.font.setFamily(QtCore.QString.fromUtf8("Helvetica"))
        self.font.setBold(True)
        self.font.setPointSize(20)

	# Create user-name label
        self.armed=QtGui.QLabel(self)
        self.armed.setFont(self.font)
        self.armed.setText("LED Controls")
	self.armed.setStyleSheet("color: blue")
        
        # put buttons + status in a vbox
        self.LEDon=QtGui.QPushButton("LEDs On",self)
        self.LEDon.clicked.connect(self.LEDsOn)

        self.LEDoff=QtGui.QPushButton("LEDs Off",self)
        self.LEDoff.clicked.connect(self.LEDsOff)
        
        # put buttons + status in a vbox
        self.goback=QtGui.QPushButton("Back",self)
        self.goback.clicked.connect(self.goBack)
        
        wid = QtGui.QWidget(self)
	vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.armed)
        vbox.addWidget(self.LEDon)
        vbox.addWidget(self.LEDoff)
        vbox.addWidget(self.goback)
	wid.setLayout(vbox)
        self.setCentralWidget(wid)

        # set to armed
        self.setGeometry(50,50,600,400)
        self.setWindowTitle('System LED control')



    def LEDsOn(self):
        self.armed.setText("TODO Set LEDs ON")



    def LEDsOff(self):
        self.armed.setText("TODO Set LEDs OFF")



    def goBack(self):
        self.parent.window_state = WindowState.MAIN_WINDOW
        self.parent.set_window_to_state()



    def teardown(self):
        self.close()

