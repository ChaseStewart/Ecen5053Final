#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys, json, numpy
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from helpers import WindowState



class LockedWindow(QtGui.QMainWindow):
    """
    This is the window that should be shown when the device is locked
    It has no functionality at all- Duhhh!
    """

    def __init__(self, parent=None):
        """
        initialize this window
        """
	super(LockedWindow, self).__init__(parent)
        self.initUI()



    def initUI(self):
        """
        Initialize the UI to simply show that the system is armed
        """

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
        wid = QtGui.QWidget(self)
	vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.armed)
	wid.setLayout(vbox)
        self.setCentralWidget(wid)

        # set to armed
        self.setGeometry(50,50,600,400)
        self.setWindowTitle('System is Armed')



    def teardown(self):
        """
        Remove this class when torn down
        """

        self.close()

