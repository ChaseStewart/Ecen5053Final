#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, json, numpy
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from boto3.session import Session

import fingerpi as fp
from Verify import verifier
from Delete import Deleting
from helpers import AccessState
from customwindow import CustomMessageBox
import time

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

        # create QT font
        font = QtGui.QFont()
        font.setFamily(QtCore.QString.fromUtf8("FreeMono"))
        font.setBold(True)
        font.setPointSize(20)

        #add background image
        palette	= QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Background,QtGui.QBrush(QtGui.QPixmap("/home/pi/Ecen5053Final/Access_RPi/enroll.jpg")))
        self.setPalette(palette)

        #create Add User button
        self.addUser_btn=QtGui.QPushButton("Add User",self)
        self.addUser_btn.clicked.connect(self.Enroll)

        #create Delete User button
        self.deleteUser_btn=QtGui.QPushButton("Delete User",self)
        self.deleteUser_btn.clicked.connect(self.Delete)

        #create Goback button
        self.goback_btn=QtGui.QPushButton("Logout",self)
        self.goback_btn.clicked.connect(self.goBack)

        #create label to display loggedin user
        self.instructions = QtGui.QLabel(self)
        self.instructions.setFont(font)
        self.instructions.setText("")
        self.instructions.setStyleSheet("color: white")
        
        #create label for username
        self.name_lbl=QtGui.QLabel(self)
        self.name_lbl.setText("Name")
        self.name_lbl.setStyleSheet("color: white")

        #create Lineedit for username
        self.Enteredname=QtGui.QLineEdit(self)
        self.Enteredname.setPlaceholderText("Enter user name")

        #Vbox for all buttons
        self.buttonbox=QtGui.QVBoxLayout()
        self.buttonbox.addWidget(self.addUser_btn)
        self.buttonbox.addWidget(self.deleteUser_btn)
        self.buttonbox.addWidget(self.goback_btn)

        #Hbox for labels
        self.Labelbox = QtGui.QHBoxLayout()
        self.Labelbox.addWidget(self.name_lbl)
        self.Labelbox.addWidget(self.Enteredname)

        #add layouts   
        self.hBox=QtGui.QHBoxLayout()
        self.hBox.addLayout(self.Labelbox)
        self.hBox.addLayout(self.buttonbox)
        self.outerBox = QtGui.QVBoxLayout()
        self.outerBox.addWidget(self.instructions)
        self.outerBox.addLayout(self.hBox)

        #set Layout
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(self.outerBox)
        self.setGeometry(50,50,600,400)


    def Enroll(self):
        """
        Add a new fingerprint into both the AWS backend and FPi sensor
        """
        self.Enroll_result = self.runscript()
        if self.Enroll_result is None:
            self.statusBar().showMessage("Registration Unsuccessful")	
        else:
            self.statusBar().showMessage("Registration Successful")
            self.parent.pubaddFingerprint(self.Enteredname.text(),self.Enroll_result)
        


    def Delete(self):
        """
        Delete a fingerprint from both AWS backend and FPi sensor
        """
        self.parent.pubrmFingerprint(self.Enteredname.text())



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


    def runscript(self):
        """
        Enroll the finger print
        """
        f = fp.FingerPi()
        ID=1 # id for the fingerprint
        f.Open(extra_info = True, check_baudrate = True)    
        f.ChangeBaudrate(115200)
        f.CmosLed(True)
        response = f.GetEnrollCount() # get number of enrolled fingerprints
        if response[0]['ACK']:
            ID=response[0]['Parameter']
            ID=ID+1
            print  ID
        self.instructions.setText("Place finger on scanner")
        self.instructions.repaint()
        time.sleep(1)

        # Enroll start sends the ID for the finger print to be scanned
        while True:
            response = f.EnrollStart(ID)
            if response[0]['ACK']:
                self.instructions.setText("Wait...")
                self.instructions.repaint()
                time.sleep(1)
                break
            else:
                print 'error',response[0]['Parameter']

        self.instructions.setText("Remove finger from scanner")
        self.instructions.repaint()
        time.sleep(1)

        #before enrolling check whether finger is pressed
        while True:
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
                    time.sleep(0.3)
		    break    

        #scan the fingerprint
        while True:
            response = f.CaptureFinger()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']

        #saving the scanned image for the first time
        while True:
            response = f.Enroll1()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']
		break

        self.instructions.setText("Place finger from scanner again")
        self.instructions.repaint()
        time.sleep(1)

        #before scanning for 2nd time check whether finger is removed
        while True:
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
                    time.sleep(1)
		else:
		    break
		
        self.instructions.setText("Remove finger on scanner again")
        self.instructions.repaint()
        time.sleep(1)

        # now placing finger on scanner 2nd time        
        while True:
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
		    break

        #scan the finger for 2nd time
        while True:
            response = f.CaptureFinger()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']

        #saving the scanned image 2nd time
        while True:
            response = f.Enroll2()
            if response[0]['ACK']:
                break
            else:
		print 'error',response[0]['Parameter']
		break

        self.instructions.setText("Place finger from scanner final time")
        self.instructions.repaint()

        #check if finger is removed from the scanner
        while True:
            response = f.IsPressFinger()
            if response[0]['Parameter']==0:
		time.sleep(1)
            else:
		break
	    
        self.instructions.setText("Remove finger on scanner final time")
        self.instructions.repaint()
        time.sleep(1)


        #check if finger is pressed for the 3rd time
        while True:
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
		    break

        #scan the finger 
        while True:
            response = f.CaptureFinger()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']
		break


        self.instructions.setText("Complete!")
        self.instructions.repaint()
        time.sleep(1)


        #save the image and combine them with other images 
        while True:
            response = f.Enroll3()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']
		return None
		break

        f.CmosLed(False)   
        print 'Closing connection...'
        f.Close()
        return ID

