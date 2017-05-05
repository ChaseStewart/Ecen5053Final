#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys, json, numpy
import opc
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from boto3.session import Session

from time import time, sleep

# all windows
from helpers import WindowState, VoiceState
from lockedwindow import LockedWindow
from ledwindow import LEDWindow
from statswindow import StatsWindow
from hub_voice import Hub_voice



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
        self.window_state = None
        self.logged_in_user = ""
        self.start_armed = True

        # set windows
        self.lockscreen  = None
        self.ledscreen   = None
        self.statsscreen = None
        self.hub_voice   = None

	# connection variables
        self.first_time  = True
        self.red         = 0
        self.green       = 0
        self.blue        = 0

	# LED vars
	self.num_pixels      = 60
	self.led_addr        = 'localhost:7890'
	self.led_client      = opc.Client(self.led_addr)
	self.fast_transition = True

	# initalize the GUI
        self.initUI()

        self.rootCAPath="/home/pi/Desktop/root-CA.crt"
        self.privateKeyPath="/home/pi/Desktop/Access01.private.key"
        self.certificatePath="/home/pi/Desktop/Access01.cert.pem"
        self.host="a1qhmcyp5eh8yq.iot.us-west-2.amazonaws.com"
        self.setupAWS()

        self.WORK_PERIOD = 2000 
        self.myTimer = QTimer()
        self.myTimer.timeout.connect(self.processSQS)
        self.myTimer.start(self.WORK_PERIOD)

	if self.led_client.can_connect():
		print('Connected to: '+self.led_addr)
	else:
		print('NOT Connected to: '+self.led_addr)


        self.window_state = WindowState.LOCK_WINDOW
        self.set_window_to_state()



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


    def set_window_to_state(self):
        """
        Select a window to display using enums from Helpers
        """

	""" FIRST PERFORM TEARDOWN """
        print("Changing state to %d" % self.window_state)

        if self.lockscreen != None and self.window_state != WindowState.LOCK_WINDOW:
            print("Hiding Lockscreen")
            self.lockscreen.teardown()
            self.lockscreen = None

        if self.window_state != WindowState.MAIN_WINDOW and self.window_state != WindowState.VOICE_WINDOW:
            if self.start_armed:
                self.start_armed = False
            else:
                print("Hiding Main")
                self.hide()

        if self.ledscreen != None and self.window_state != WindowState.LED_WINDOW:
            print("Hiding LEDscreen")
            self.ledscreen.teardown()
            self.ledscreen = None

        if self.statsscreen != None and self.window_state != WindowState.STATS_WINDOW:
            print("Hiding Statsscreen")
            self.statsscreen.teardown()
            self.statsscreen = None



	""" NOW SET DATA FOR CURRENT WINDOW """

        if self.window_state == WindowState.LOCK_WINDOW and self.lockscreen == None:
            print("Showing Lockscreen")
            self.lockscreen = LockedWindow(self)
            self.lockscreen.show()

        if self.window_state == WindowState.MAIN_WINDOW:
            print("Showing Main")
            self.show()
            self.LED_btn.show()
            self.Voice_btn.show()
            self.Stats_btn.show()
            self.Logout_btn.show()

        if self.window_state == WindowState.VOICE_WINDOW:
            print("Hiding Buttons")
            self.LED_btn.hide()
            self.Voice_btn.hide()
            self.Stats_btn.hide()
            self.Logout_btn.hide()

        if self.window_state == WindowState.LED_WINDOW and self.ledscreen == None:
            print("Showing LEDscreen")
            self.ledscreen = LEDWindow(self)
            self.ledscreen.show()

        if self.window_state == WindowState.STATS_WINDOW and self.statsscreen == None:
            print("Showing Statscreen")
            self.statsscreen = StatsWindow(self)
            self.statsscreen.show()



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

		# process login type messages and set access state
		if json_body['type'] == 'login':               
 
			arm_state = json_body['arm_state']
			my_user   = json_body['username']
			access    = json_body['access']       

			self.logged_in_user = my_user    
			self.access = int(access)

			if arm_state == "Armed":
			    self.window_state = WindowState.LOCK_WINDOW
			    self.set_window_to_state()

			else:
			    self.user_data.setText("Welcome, "+str(self.logged_in_user))
			    self.window_state = WindowState.MAIN_WINDOW 
			    self.set_window_to_state()

		# process overhead type messages and set latency
		elif json_body['type'] == 'overhead':
			if self.window_state == WindowState.STATS_WINDOW:
				self.ws_latency   = json_body['ws_lat']
				self.mqtt_latency = json_body['mqtt_lat']
				self.coap_latency = json_body['coap_lat']

        			# call update to stats grpah
				if self.statsscreen != None:
					self.statsscreen.latencyStats(self.ws_latency, self.coap_latency, self.mqtt_latency)

		# process LED type messages and send websocket to FCServer
		elif json_body['type'] == 'led':
			if self.window_state != WindowState.LOCK_WINDOW:
				self.red   = json_body['red']
				self.blue  = json_body['blue']
				self.green = json_body['green']

				# format and send WS message
				self.setLEDs(self.red, self.green, self.blue)

            # Now delete the ack'ed message
            for item in acked_messages:
                self.client.delete_message(QueueUrl=self.queue, ReceiptHandle=item)
            return self.logged_in_user

        # otherwise just return
        else:
            return


 
    def initUI(self):
        """ 
        Initialize + configure all QT modules used in the GUI
        And place them on the screen in the application
        """
        #add background image
        palette	= QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Background,QtGui.QBrush(QtGui.QPixmap("/home/pi/Ecen5053Final/Assets/Hub/background.png")))
        self.setPalette(palette)

	
	# create QT font
        font = QtGui.QFont()
        font.setFamily(QtCore.QString.fromUtf8("Helvetica"))
        font.setBold(True)
        font.setPointSize(20)

	# Create user-name label
        self.user_data=QtGui.QLabel(self)
        self.user_data.setFont(font)
        self.user_data.setStyleSheet("color: white")
        self.user_data.setText("No Logged In User")

        # Create voice_status label
        self.voice_status=QtGui.QLabel(self)
        self.voice_status.setFont(font)
        self.voice_status.setStyleSheet("color: white")
        self.voice_status.setText("Voice Mode off")

	# Create status bar
	self.statusBar()
	self.statusBar().setStyleSheet("color: red; font-size:18pt")

	# Create LED button
	self.LED_btn=QtGui.QPushButton("LED Settings",self)
        self.LED_btn.clicked.connect(self.setLEDPage)

        # Create Voice mode button
	self.Voice_btn=QtGui.QPushButton("Voice Mode",self)
        self.Voice_btn.clicked.connect(self.setVoicemode)

	# Create Stats button        
	self.Stats_btn=QtGui.QPushButton("System Stats",self)
        self.Stats_btn.clicked.connect(self.setStatsPage)
	
        # Create Logout button        
	self.Logout_btn=QtGui.QPushButton("Logout",self)
        self.Logout_btn.clicked.connect(self.setLogoutPage)

	# Now create layout
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)

	# put buttons in an hbox
	vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(self.LED_btn)
        vbox2.addWidget(self.Voice_btn)
        vbox2.addWidget(self.Stats_btn)
        vbox2.addWidget(self.Logout_btn)
        
	# put buttons + status in a vbox
	vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.user_data)
        vbox.addWidget(self.voice_status)
    
        # combine layouts
        vbox.addLayout(vbox2)
	wid.setLayout(vbox)

        self.setGeometry(50,50,600,400)
        self.setWindowTitle('Main Page')
        self.show()



    def setStatsPage(self):
        """
        Change the state of the Arm_status table in MySQL to 'armed'
        """
        self.window_state = WindowState.STATS_WINDOW
        self.set_window_to_state()



    def setLEDPage(self):
        """
        Change the state of the Arm_status table in MySQL to 'disarmed'
        """
        self.window_state = WindowState.LED_WINDOW
        self.set_window_to_state()


    
    def setVoicemode(self):
        """
        Switching the voice mode on
        """
        
        self.voice_status.setText("Voice Mode ON")
        self.voice_status.repaint()
        self.hub_voice = Hub_voice(self)
        
	# change state to VOICE and set window
	self.window_state = WindowState.VOICE_WINDOW
        self.set_window_to_state()
        
        # set timer for first time'   
        QtCore.QTimer.singleShot(50, self.listenAgain) 


 
    def listenAgain(self):
	"""
	Use a timer to give the the app time to process SQS messages between voice commands
	"""
        
	# first listen
        self.hub_voice.listen_once()

	# if the command was not "end voice", schedule another listen
	print("Hub voice State is "+str(self.hub_voice.IS_RUNNING))
        if self.hub_voice.IS_RUNNING == VoiceState.RUNNING:
            # set timer to run again
            QtCore.QTimer.singleShot(400, self.listenAgain) 

        elif self.hub_voice.IS_RUNNING == VoiceState.ERROR:
            print ("Voice error")
            
            self.voice_status.setText("Problem with mic")
            self.voice_status.repaint()
            sleep(2)
            self.window_state = WindowState.MAIN_WINDOW
            self.set_window_to_state()
            self.voice_status.setText("Voice Mode OFF")

	# if the command was "end voice", show the buttons again and change state to MAIN
        else:       
	    self.window_state = WindowState.MAIN_WINDOW
            self.set_window_to_state()
            
            self.voice_status.setText("Voice Mode OFF")


 
    def setLogoutPage(self):
        """
        Change the state of the Arm_status table in MySQL to 'disarmed'
        """
        self.myAWSIoTMQTTClient.publish("AccessControl/UserPass", json.dumps({"user_name":"","password":""}), 1)
        self.window_state = WindowState.LOCK_WINDOW
        self.set_window_to_state()



    def setLEDs(self, red, green, blue):
	"""
	Take a RGB tuple, set that value for all 60 LEDs in the strip
	"""

	out_list = []
        my_tuple = (red, green, blue)
	
	# create a list of tuples for WS output
	for i in range(self.num_pixels):
            out_list.append(my_tuple)
	
	# now try to send pixels to FCserver, else fail gracefully
	if self.led_client.put_pixels(out_list, channel=0):
		pass
	else:
		print("Not connected!")

	# if using fast transition, double-send LEDs 
	if self.fast_transition:	
		if self.led_client.put_pixels(out_list, channel=0):
			pass
		else:
			print("Not connected!")
	return




if __name__ == "__main__":
    """ Run program if called as main function """
    app = QtGui.QApplication(sys.argv)
    try:
        hub=Hub()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        sys.exit(-1) 
