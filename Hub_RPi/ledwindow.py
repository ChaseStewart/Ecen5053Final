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
	super(LockedWindow, self).__init__(parent)
        self.initUI()



    def initUI(self):

	# create QT font
        self.font = QtGui.QFont()
        self.font.setFamily(QtCore.QString.fromUtf8("Helvetica"))
        self.font.setBold(True)
        self.font.setPointSize(20)

	# Create user-name label
        self.armed=QtGui.QLabel(self)
        self.armed.setFont(self.font)
        self.armed.setText("System is ARMED")
	self.armed.setStyleSheet("color: red")
        
        # put buttons + status in a vbox
        self.LEDon=QtGui.QPushButton("LEDs On",self)
        self.LEDon.clicked.connect(self.Enroll)

        self.LEDoff=QtGui.QPushButton("LEDs Off",self)
        self.LEDoff.clicked.connect(self.Delete)
        
        wid = QtGui.QWidget(self)
	vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.armed)
        vbox.addWidget(self.LEDon)
        vbox.addWidget(self.LEDoff)
	wid.setLayout(vbox)
        self.setCentralWidget(wid)

        # set to armed
        self.setGeometry(50,50,600,400)
        self.setWindowTitle('System is Armed')


    def teardown(self):
        self.close()

