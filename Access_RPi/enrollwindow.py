#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, json, numpy
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from boto3.session import Session

#import fingerpi as fpi
from Verify import verifier
from Enroll import enrolling
from Delete import Deleting
from helpers import AccessState


class EnrollWindow(QtGui.QMainWindow):
    """
    This is the window that's shown after the user authenticates
    It allows the user to logout, add a fingerprint, or remove a fingerprint
    """
    def __init__(self,parent=None):
        super(EnrollWindow,self).__init__(parent)

        self.parent = parent
                
        self.Enroll_result= None
        self.Delete_result=None
        self.initUI()



    def initUI(self):
        """
        Create the graphical UI
        """

        self.addUser_btn=QtGui.QPushButton("Add User",self)
        self.addUser_btn.clicked.connect(self.Enroll)
        
        self.deleteUser_btn=QtGui.QPushButton("Delete User",self)
        self.deleteUser_btn.clicked.connect(self.Delete)
        
        self.goback_btn=QtGui.QPushButton("Logout",self)
        self.goback_btn.clicked.connect(self.goBack)

        self.name_lbl=QtGui.QLabel(self)
        self.name_lbl.setText("Name")

        self.Enteredname=QtGui.QLineEdit(self)
        self.Enteredname.setPlaceholderText("Enter user name")

        self.buttonbox=QtGui.QVBoxLayout()
        self.buttonbox.addWidget(self.addUser_btn)
        self.buttonbox.addWidget(self.deleteUser_btn)
        self.buttonbox.addWidget(self.goback_btn)
        self.Labelbox = QtGui.QHBoxLayout()
        self.Labelbox.addWidget(self.name_lbl)
        self.Labelbox.addWidget(self.Enteredname)
        self.hBox=QtGui.QHBoxLayout()
        self.hBox.addLayout(self.Labelbox)
        self.hBox.addLayout(self.buttonbox)
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(self.hBox)
        self.setGeometry(50,50,600,400)



    def Enroll(self):
        """
        Add a new fingerprint into both the AWS backend and FPi sensor
        """

        my_Enroll = enrolling()
        self.Enroll_result = my_Enroll.runscript()
        if self.Enroll_result is None:
            self.statusBar().showMessage("Registration Unsuccessful")	
        else:
            self.statusBar().showMessage("Registration Successful")
            access.pubaddFingerprint(self.Enteredname.text(),self.Enroll_result)
           


    def Delete(self):
        """
        Delete a fingerprint from both AWS backend and FPi sensor
        """
        access.pubrmFingerprint(self.Enteredname.text())



    def teardown(self):
        """
        Simply close this window
        """

        self.close()



    def goBack(self):
        """
        close this and return to being armed
        """

        self.parent.myAWSIoTMQTTClient.publish("AccessControl/UserPass", json.dumps({"user_name":"","password":""}), 1)
        self.parent.window_state = AccessState.ARM_WINDOW
        self.parent.set_window_to_state()

