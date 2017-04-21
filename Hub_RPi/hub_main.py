#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys, json, numpy
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from boto3.session import Session


from helpers import WindowState
from lockedwindow import LockedWindow
from ledwindow import LEDWindow


#class LockedWindow(QtGui.QMainWindow):
#    """
#    This is the window that should be shown when the device is locked
#    """
#
#    def __init__(self, parent=None):
#        """
#        initialize this window
#        """
#	super(LockedWindow, self).__init__(parent)
#        self.initUI()
#
#
#
#    def initUI(self):
#
#	# create QT font
#        self.font = QtGui.QFont()
#        self.font.setFamily(QtCore.QString.fromUtf8("Helvetica"))
#        self.font.setBold(True)
#        self.font.setPointSize(20)
#
#	# Create user-name label
#        self.armed=QtGui.QLabel(self)
#        self.armed.setFont(self.font)
#        self.armed.setText("System is ARMED")
#	self.armed.setStyleSheet("color: red")
#        
#
#        # put buttons + status in a vbox
#        wid = QtGui.QWidget(self)
#	vbox = QtGui.QVBoxLayout()
#        vbox.addWidget(self.armed)
#	wid.setLayout(vbox)
#        self.setCentralWidget(wid)
#
#        # set to armed
#        self.setGeometry(50,50,600,400)
#        self.setWindowTitle('System is Armed')
#
#
#    def teardown(self):
#        self.close()


class Hub(QtGui.QMainWindow):
    """
    The top-level class of the project2 Hub R Pi GUI-
    Controls everything on the R Pi for this demo
    """

    def __init__(self, use_websockets=False):
        """
        Setup the GUI, setup the Websockets Connection,
        provide timer and button callback updates, and display info
        """

        super(Hub,self).__init__()
        self.use_websockets=use_websockets

        # set access ctl
	self.access   = 0
        self.my_state = None


	# connection variables
        self.url = "ws://52.34.209.113:8080/websocket"
        self.ws_timeout  = 500
        self.gui_timeout = 250 
        self.first_time=True
        self.drop_count = 0
        self.toggle = 0

	# Tornado Variables
        self.ioloop = IOLoop.instance()
        self.ws = None

	# initalize the GUI
        self.initUI()

        if self.use_websockets:
	    # Connect to the Websockets server
            self.connect()
	    
	    # setup the Websocket IO Loop
	    self.my_p_callback = PeriodicCallback(self.keep_alive, self.ws_timeout, io_loop=self.ioloop)
	    self.my_p_callback.start()
            self.ioloop.start()

        else:
            self.rootCAPath="/home/pi/Desktop/root-CA.crt"
            self.privateKeyPath="/home/pi/Desktop/Access01.private.key"
            self.certificatePath="/home/pi/Desktop/Access01.cert.pem"
            self.host="a1qhmcyp5eh8yq.iot.us-west-2.amazonaws.com"

            self.setupAWS()
  
            self.WORK_PERIOD = 2000 
            self.myTimer = QTimer()
            self.myTimer.timeout.connect(self.processSQS)
            self.myTimer.start(self.WORK_PERIOD)

        self.set_locked()

    def setupAWS(self):

        # Setup AWS IoT basics
        self.myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
        self.myAWSIoTMQTTClient.configureEndpoint(self.host, 8883)
        self.myAWSIoTMQTTClient.configureCredentials(self.rootCAPath, self.privateKeyPath, self.certificatePath)

        # AWSIoTMQTTClient connection configuration
        self.myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        self.myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        self.myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        
        # Connect and subscribe to AWS IoT
        self.myAWSIoTMQTTClient.connect()

	# Connect to the SQS Queue
        try:
            self.session = Session()
        except:
            print("Need to configure AWS- exit and run 'aws configure' ")
            sys.exit(-1)
        
        self.client  = self.session.client('sqs')
	self.queue   = self.client.get_queue_url(QueueName="Hub_Messages")['QueueUrl']


    def set_locked(self):
        self.lockscreen = LockedWindow(self)
        self.lockscreen.show()
        self.hide()
        self.my_state = WindowState.LOCK_WINDOW


    def processSQS(self):
        """
        Process messages from the queue
        """

        acked_messages = []
        

        # Pull Messages
        self.messages = self.client.receive_message( 
            QueueUrl = self.queue,
            AttributeNames = ['ReceiptHandle','body'],
            MaxNumberOfMessages = 10,
            VisibilityTimeout = 60,
            WaitTimeSeconds = 1	)

        # Handle message
        if self.messages.get('Messages'):
            m = self.messages.get('Messages')
            for msg in m:
                body   = msg['Body']
                acked_messages.append(msg['ReceiptHandle'])
		print body
                json_body = json.loads(body)
                
                arm_state = json_body['arm_state']
                my_user   = json_body['username']
                access    = json_body['access']       
    
                self.access = int(access)

                if arm_state == "Armed":
                    if self.lockscreen == None:
                        self.set_locked()

                else:
		    self.user_data.setText("Welcome, "+str(my_user))

                    if self.lockscreen != None:
                        self.lockscreen.teardown()
                        self.lockscreen = None
                        self.show()

            # Now delete the ack'ed message
            for item in acked_messages:
                self.client.delete_message(QueueUrl=self.queue, ReceiptHandle=item)

        # otherwise just return
        else:
            return


 
    def initUI(self):
        """ 
        Initialize + configure all QT modules used in the GUI
        And place them on the screen in the application
        """
	
	# create QT font
        font = QtGui.QFont()
        font.setFamily(QtCore.QString.fromUtf8("Helvetica"))
        font.setBold(True)
        font.setPointSize(20)

	# Create user-name label
        self.user_data=QtGui.QLabel(self)
        self.user_data.setFont(font)
        self.user_data.setText("No Logged In User")

	# Create alarm-state label
        self.state=QtGui.QLabel(self)
        self.state.setFont(font)
        self.state.setText("Arm state is: Armed")
	self.state.setStyleSheet("color: blue")

	# Create status bar
	self.statusBar()
	self.statusBar().setStyleSheet("color: red; font-size:18pt")

	# Create Arm button        
	self.Arm_btn=QtGui.QPushButton("LEDs On",self)
        self.Arm_btn.clicked.connect(self.sendLEDsOn)
        self.Arm_btn.hide()

	# Create Disarm button        
	self.Disarm_btn=QtGui.QPushButton("LEDs Off",self)
        self.Disarm_btn.clicked.connect(self.sendLEDsOff)
        self.Disarm_btn.hide()

	# Now create layout
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)

	# put buttons in an hbox
	hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.Arm_btn)
        hbox.addWidget(self.Disarm_btn)
        
	# put buttons + status in a vbox
	vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.user_data)
        vbox.addWidget(self.state)
    
        # combine layouts
        vbox.addLayout(hbox)
	wid.setLayout(vbox)

        self.setGeometry(50,50,600,400)
        self.setWindowTitle('Project 2 Demo')
        self.show()


        
    def sendLEDsOn(self):
        """
        Change the state of the Arm_status table in MySQL to 'armed'
        """

        print("TODO SET LEDS ON")
        self.state.setText('Would have set LEDs ON')
        if self.ws is None:
            pass
        else:
            print("ARM SYSTEM")        
            #self.ws.write_message("set_arm")


    def sendLEDsOff(self):
        """
        Change the state of the Arm_status table in MySQL to 'disarmed'
        """

        self.state.setText('Would have set LEDs OFF')
        print("TODO SET LEDS OFF")
        if self.ws is None:
            #self.connect()
            pass
        else:
            print("DISARM SYSTEM")        
            self.ws.write_message("set_dis")

        
    @gen.coroutine
    def connect(self):
        """
        Connect to the websockets server
        on our ec2 server
        """

        #print "trying to connect"

        try:
            self.ws = yield websocket_connect(self.url)
        except Exception, e:
            print "connection error"
        else:
            #print "connected"
            pass


    def sendAndRead(self):
        """ 
        query for login and arm/disarm status and read responses
        """

        #print("Sending messages!")
        self.toggle = 1 - self.toggle

        if self.toggle == 1:
		self.ws.write_message("login_status")
		self.readInput()
        else:
		self.ws.write_message("arm_status")
		self.readInput()



    @gen.coroutine
    def readInput(self):
        """
        read a message back from websockets and set update
        """
 
        try:
            msg = yield self.ws.read_message()
        except:
            self.drop_count += 1
            if self.drop_count >= 2:
		    self.statusBar().showMessage('Connection Error!')
                    self.user_data.setText("Disconnected!")
                    self.state.setText("")
            return

        self.drop_count = 0

        # data is sent 
        self.statusBar().clearMessage()
        indata = msg.split(":")
        if indata[0] == "name" :
            self.user_data.setText("Welcome, "+indata[1])
        elif indata[0] == "state" :
            self.state.setText("Arm/Disarm state is: "+indata[1])
        #print ("Received Data: '"+indata[1]+"'")


        
    def keep_alive(self):
        """ 
        heartbeat function of program- send commands
        and receive data to display
        """
        
        # reconnect if connection has been lost
        if self.ws is None:
            self.connect()
        else:
            if self.first_time:
                self.first_time = False
            else:
                try:
                    self.ioloop.start()
                except:
                    self.connect()
            
            self.sendAndRead()
            
            self.ioloop.stop()
            self.my_p_callback.stop()
            QTimer.singleShot(self.gui_timeout, self.poll_websockets)
            

    def poll_websockets(self):
        """ Take control from GUI for websockets"""

        self.my_p_callback.start()
        self.ioloop.start()


if __name__ == "__main__":
    """ Run program if called as main function """
    app = QtGui.QApplication(sys.argv)
    hub=Hub()
    sys.exit(app.exec_())
