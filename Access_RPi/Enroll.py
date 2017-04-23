#!/usr/bin/env python

import fingerpi as fp
import time
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QTimer
import sys

class CustomMessageBox(QtGui.QMessageBox):
    def __init__(self, *__args):
        QtGui.QMessageBox.__init__(self)
        self.timeout = 0
        self.autoclose = False
        self.currentTime = 0

    def showEvent(self, QShowEvent):
        self.currentTime = 0
        if self.autoclose:
            self.startTimer(1000)

    def timerEvent(self, *args, **kwargs):
        self.currentTime += 1
        if self.currentTime >= self.timeout:
            self.done(0)

    @staticmethod
    def showWithTimeout(timeoutSeconds, message, title, icon=QtGui.QMessageBox.Information, buttons=QtGui.QMessageBox.Ok):
        w = CustomMessageBox()
        w.autoclose = True
        w.timeout = timeoutSeconds
        w.setText(message)
        w.setWindowTitle(title)
        w.setIcon(icon)
        w.setStandardButtons(buttons)
        w.exec_()

class enrolling:
    def __init__(self):
          pass
##        self.WORK_PERIOD = 1000 
##        self.myTimer = QTimer()
##        self.myTimer.timeout.connect(self.closedialog)
##        
##    def closedialog(self):
##        sys.exit()
##    def showdialog(self,text):
##
##        msg = QtGui.QMessageBox()
##        msg.setIcon(QtGui.QMessageBox.Information)
##        msg.setText(text)
##        #msg.setStandardButtons(QtGui.QMessageBox.NoButton)
##        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
##        msg.exec_()
##        #msg.show()
    def runscript(self):
    
        f = fp.FingerPi()
        i=1
        #self.showdialog('Opening connection')
        print 'Opening connection...'
        f.Open(extra_info = True, check_baudrate = True)
        #self.dialog.hide()
        print 'Change baudrate'
        f.ChangeBaudrate(115200)
        f.CmosLed(True)


        response = f.GetEnrollCount()
        if response[0]['ACK']:
            i=response[0]['Parameter']
            i=i+1
            print  i
        while True:
            #self.myTimer.start(self.WORK_PERIOD)
            #self.showdialog('Start Enrollment')
            #print 'start enrolling'
            CustomMessageBox.showWithTimeout(2, "Start Enrollment", "Instructions", icon=QtGui.QMessageBox.Information)
            response = f.EnrollStart(i)
            if response[0]['ACK']:
                break
            else:
                print 'error',response[0]['Parameter']
        CustomMessageBox.showWithTimeout(2, "Place the finger on the scanner", "Instructions", icon=QtGui.QMessageBox.Information)
        #print 'Place the finger on the scanner'
        while True:
            print 'IspressFinger'
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
                    time.sleep(3)
		    break    
        while True:
            print 'captureFinger'
            response = f.CaptureFinger()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']
        CustomMessageBox.showWithTimeout(2, "Remove the finger", "Instructions", icon=QtGui.QMessageBox.Information)
        #print 'Remove Finger'
        while True:
            print 'Enrollment 1'
            response = f.Enroll1()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']
		break
	CustomMessageBox.showWithTimeout(2, "Scanned Once", "Instructions", icon=QtGui.QMessageBox.Information)
        while True:
            print 'IspressFinger'
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
                    CustomMessageBox.showWithTimeout(2, "Remove the finger", "Instructions", icon=QtGui.QMessageBox.Information)
		    #print 'Remove the finger'
		else:
		    time.sleep(3)
		    break
        CustomMessageBox.showWithTimeout(2, "Place the finger on the scanner", "Instructions", icon=QtGui.QMessageBox.Information)
        #print 'Place the finger on the scanner'
        while True:
            print 'IspressFinger'
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
		    time.sleep(3)
		    break
        while True:
            response = f.CaptureFinger()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']
        CustomMessageBox.showWithTimeout(2, "Remove the finger", "Instructions", icon=QtGui.QMessageBox.Information)
        #print 'Remove your finger'
        while True:
            print 'Enrollment 2'
            response = f.Enroll2()
            if response[0]['ACK']:
                break
            else:
		print 'error',response[0]['Parameter']
		break
	CustomMessageBox.showWithTimeout(2, "Scanned twice", "Instructions", icon=QtGui.QMessageBox.Information)
        while True:
            print 'IspressFinger'
            response = f.IsPressFinger()
            if response[0]['Parameter']==0:
                CustomMessageBox.showWithTimeout(2, "Remove the finger ", "Instructions", icon=QtGui.QMessageBox.Information)
		#print 'Remove the finger'
            else:
		time.sleep(3)
		break
        CustomMessageBox.showWithTimeout(2, "Place the finger on the scanner", "Instructions", icon=QtGui.QMessageBox.Information)
        #print 'Place the finger on the scanner'
        while True:
            print 'IspressFinger'
            response = f.IsPressFinger()
            if response[0]['ACK']:
		if response[0]['Parameter']==0:
		    time.sleep(3)
		    break
        while True:
            response = f.CaptureFinger()
            if response[0]['ACK']:
		break
            else:
		print 'error',response[0]['Parameter']
		break
        CustomMessageBox.showWithTimeout(2, "Remove the finger", "Instructions", icon=QtGui.QMessageBox.Information)
        #print 'Remove finger'
        while True:
            print 'Enrollment 3'
            response = f.Enroll3()
            if response[0]['ACK']:
		#print 'registration completed'
		CustomMessageBox.showWithTimeout(2, "Registration Completed", "Instructions", icon=QtGui.QMessageBox.Information)
		break
            else:
		print 'error',response[0]['Parameter']
		return None
		break
        f.CmosLed(False)   
        print 'Closing connection...'
        f.Close()
        return i
