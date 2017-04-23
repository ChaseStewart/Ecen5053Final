#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys, json, numpy
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from helpers import WindowState


class StatsWindow(QtGui.QMainWindow):
    """
    This is the window that should be shown when the device is locked
    """

    def __init__(self, parent=None):
        """
        initialize this window
        """
	super(StatsWindow, self).__init__(parent)
        self.initUI()
        self.parent = parent



    def initUI(self):

	# create QT font
        self.font = QtGui.QFont()
        self.font.setFamily(QtCore.QString.fromUtf8("Helvetica"))
        self.font.setBold(True)
        self.font.setPointSize(20)

	# Create user-name label
        self.stats=QtGui.QLabel(self)
        self.stats.setFont(self.font)
        self.stats.setText("System Stats")
        
        # put buttons + status in a vbox
        self.todo=QtGui.QPushButton("TODO",self)
        self.todo.clicked.connect(self.printStats)
        
        # put buttons + status in a vbox
        self.goback=QtGui.QPushButton("Back",self)
        self.goback.clicked.connect(self.goBack)

        wid = QtGui.QWidget(self)
	vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.stats)
        vbox.addWidget(self.todo)
        vbox.addWidget(self.goback)
	wid.setLayout(vbox)
        self.setCentralWidget(wid)

        # set to armed
        self.setGeometry(50,50,600,400)
        self.setWindowTitle('System Stats')



    def printStats(self):
        self.stats.setText("Would have printed stats!")



    def goBack(self):
        self.parent.window_state = WindowState.MAIN_WINDOW
        self.parent.set_window_to_state()



    def teardown(self):
        self.close()

