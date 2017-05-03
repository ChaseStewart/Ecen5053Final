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

	self.red = None
	self.blue = None
	self.green = None

    def initUI(self):

	# create QT font
        self.font = QtGui.QFont()
        self.font.setFamily(QtCore.QString.fromUtf8("Helvetica"))
        self.font.setBold(True)
        self.font.setPointSize(20)

	# Create user-name label
        self.label=QtGui.QLabel(self)
        self.label.setFont(self.font)
        self.label.setText("LED Controls")
	self.label.setStyleSheet("color: blue")
        
	self.LEDredInput = QtGui.QLineEdit(self)
	self.LEDredInput.setPlaceholderText("Set red val between 0 and 255")
	self.LEDredLabel = QtGui.QLabel(self)
	self.LEDredLabel.setText("Red")
	self.LEDred = QtGui.QHBoxLayout()
	self.LEDred.addWidget(self.LEDredInput)
	self.LEDred.addWidget(self.LEDredLabel)
	
	self.LEDgreenInput = QtGui.QLineEdit(self)
	self.LEDgreenInput.setPlaceholderText("Set green val between 0 and 255")
	self.LEDgreenLabel = QtGui.QLabel(self)
	self.LEDgreenLabel.setText("Green")
	self.LEDgreen = QtGui.QHBoxLayout()
	self.LEDgreen.addWidget(self.LEDgreenInput)
	self.LEDgreen.addWidget(self.LEDgreenLabel)
	
	self.LEDblueInput = QtGui.QLineEdit(self)
	self.LEDblueInput.setPlaceholderText("Set blue val between 0 and 255")
	self.LEDblueLabel = QtGui.QLabel(self)
	self.LEDblueLabel.setText("Blue")
	self.LEDblue = QtGui.QHBoxLayout()
	self.LEDblue.addWidget(self.LEDblueInput)
	self.LEDblue.addWidget(self.LEDblueLabel)

	# create submission button
	self.submit=QtGui.QPushButton("Submit",self)
        self.submit.clicked.connect(self.SubmitLED)
        
        # put buttons + status in a vbox
        self.goback=QtGui.QPushButton("Back",self)
        self.goback.clicked.connect(self.goBack)
        
	self.statusBar()
	self.statusBar().setStyleSheet("color: red; font-size:18pt")
        
	wid = QtGui.QWidget(self)
	vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addLayout(self.LEDred)
        vbox.addLayout(self.LEDgreen)
        vbox.addLayout(self.LEDblue)
        vbox.addWidget(self.submit)
        vbox.addWidget(self.goback)
	wid.setLayout(vbox)
        self.setCentralWidget(wid)

        # set to armed
        self.setGeometry(50,50,600,400)
        self.setWindowTitle('System LED control')


    def verifyColors(self):
	if self.LEDgreenInput.text() == "" or self.LEDredInput.text() == "" or self.LEDblueInput.text() == "":
		self.statusBar().setStyleSheet("color: red; font-size:18pt")
		self.statusBar().showMessage("must fill out all three values")
		return False
	try:
		red_test   = int(self.LEDredInput.text())
		green_test = int(self.LEDgreenInput.text())
		blue_test  = int(self.LEDblueInput.text())
	except:
		self.statusBar().setStyleSheet("color: red; font-size:18pt")
		self.statusBar().showMessage("entered values must be integers")
		return False
	
	if red_test > 255 or red_test < 0:
		self.statusBar().setStyleSheet("color: red; font-size:18pt")
		self.statusBar().showMessage("Red val must be between 0 and 255")
		return False

	if green_test > 255 or green_test < 0:
		self.statusBar().setStyleSheet("color: red; font-size:18pt")
		self.statusBar().showMessage("Blue val must be between 0 and 255")
		return False

	if blue_test > 255 or blue_test < 0:
		self.statusBar().setStyleSheet("color: red; font-size:18pt")
		self.statusBar().showMessage("Green val must be between 0 and 255")
		return False
	else:
		self.red   = red_test
		self.blue  = blue_test
		self.green = green_test
		return True		


    def clearEntries(self):
        self.LEDgreenInput.clear()
        self.LEDblueInput.clear()
        self.LEDredInput.clear()

    def SubmitLED(self):
        if self.verifyColors():
            jsonData = {}
            jsonData['type']  = 'led'
            jsonData['blue']  = self.blue
            jsonData['red']   = self.red
            jsonData['green'] = self.green
            strData = json.dumps(jsonData)

            try:
                self.parent.myAWSIoTMQTTClient.publish("AccessControl/set_leds", strData, 1)
		self.statusBar().setStyleSheet("color: black; font-size:18pt")
                self.statusBar().showMessage("published successfully!")
                self.clearEntries()
            except:
		self.statusBar().setStyleSheet("color: red; font-size:18pt")
                self.statusBar().showMessage("LED publish failed!")



    def goBack(self):
        self.parent.window_state = WindowState.MAIN_WINDOW
        self.parent.set_window_to_state()



    def teardown(self):
        self.close()

