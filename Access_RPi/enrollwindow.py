#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, json, numpy
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from boto3.session import Session

import fingerpi as fp
from Verify import verifier
#from Enroll import enrolling
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

        self.addUser_btn=QtGui.QPushButton("Add User",self)
        self.addUser_btn.clicked.connect(self.Enroll)
        
        self.deleteUser_btn=QtGui.QPushButton("Delete User",self)
        self.deleteUser_btn.clicked.connect(self.Delete)
        
        self.goback_btn=QtGui.QPushButton("Logout",self)
        self.goback_btn.clicked.connect(self.goBack)

        self.instructions = QtGui.QLabel(self)
        self.instructions.setText("")
        

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
        self.outerBox = QtGui.QVBoxLayout()
        self.outerBox.addWidget(self.instructions)
        self.outerBox.addLayout(self.hBox)
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
    
        f = fp.FingerPi()
        i=1
        f.Open(extra_info = True, check_baudrate = True)    
        f.ChangeBaudrate(115200)
        f.CmosLed(True)
        response = f.GetEnrollCount()
        if response[0]['ACK']:
            i=response[0]['Parameter']
            i=i+1
            print  i
        self.instructions.setText("Place finger on scanner")
        self.instructions.repaint()
        time.sleep(1)
        
        while True:
            response = f.EnrollStart(i)
            if response[0]['ACK']:
                self.instructions.setText("Wait...")
                self.instructions.repaint()
                time.sleep(1)
                break
            else:
                print 'error',response[0]['Parameter']
                time.sleep(0.3)

        self.instructions.setText("Remove finger from scanner")
        self.instructions.repaint()
        time.sleep(1)

        while True:
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
                    time.sleep(0.3)
		    break    

        while True:
            #print 'captureFinger'
            response = f.CaptureFinger()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']

        
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

        while True:
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
                    time.sleep(1)
		else:
		    #time.sleep(1)
		    break
		
        self.instructions.setText("Remove finger on scanner again")
        self.instructions.repaint()
        time.sleep(1)

        # now placing finger on scanner 2nd time        
        while True:
            #print 'IspressFinger'
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
		    #time.sleep(3)
		    break
        while True:
            response = f.CaptureFinger()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']

        while True:
            #print 'Enrollment 2'
            response = f.Enroll2()
            if response[0]['ACK']:
                break
            else:
		print 'error',response[0]['Parameter']
		break

        self.instructions.setText("Place finger from scanner final time")
        self.instructions.repaint()

        while True:
            #print 'IspressFinger'
            response = f.IsPressFinger()
            if response[0]['Parameter']==0:
		time.sleep(1)
            else:
		time.sleep(1)
		break
	    
        self.instructions.setText("Remove finger on scanner final time")
        self.instructions.repaint()
        time.sleep(1)
        
        while True:
            #print 'IspressFinger'
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
		    #time.sleep(3)
		    break

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

        while True:
            print 'Enrollment 3'
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
        return i

