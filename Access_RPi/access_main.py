#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, json, numpy, time
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from boto3.session import Session



from helpers import AccessState
from enrollwindow import EnrollWindow
from Verify import verifier
from Delete import Deleting
from customwindow import CustomMessageBox

class Access(QtGui.QMainWindow):
    """
    The top-level class of the project2 Hub R Pi GUI-
    Controls everything on the R Pi for this demo
    """

    def __init__(self, use_websockets=False):
        """
        Setup the GUI, setup the Websockets Connection,
        provide timer and button callback updates, and display info
        """
	self.use_websockets=use_websockets

        super(Access,self).__init__()

	# connection variables
        self.ws_url = "ws://52.34.209.113:8080/websocket"
        self.ws_timeout  = 500
        self.ws_gui_timeout = 250 
        self.first_time=True
        self.drop_count = 0
        self.toggle = 0

        # access_state_vars
        self.startWithEnroll = True
        self.enrollWindow = None
        self.customWindow = None
        self.window_state = None 
        self.access = 0


	# Tornado Variables
        self.ws_ioloop = IOLoop.instance()
        self.ws = None

        # verify Variables
        self.verify_result=None

	# initalize the GUI
        self.initUI()

        # initialize the main window
        self.window_state = AccessState.ARM_WINDOW
        self.set_window_to_state()

	
        if self.use_websockets: 
            # Connect to the Websockets server
            #self.connect()
        
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



    def setupAWS(self):

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
	self.queue   = self.client.get_queue_url(QueueName="Access_Messages")['QueueUrl']



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
                json_body = json.loads(body)
                print(json_body)
                if json_body['type'] == 'rm_index':
                        user_id = json_body['user_id']
                        try:
                            my_Delete = Deleting()
                            self.Delete_result = my_Delete.runscript(user_id)
                            if self.Delete_result is None:
                                    self.statusBar().showMessage("Deletion failed")
                                    time.sleep(1)
                                    self.statusBar().clearMessage()
                            else:
                                    self.statusBar().showMessage("Deleted successfully")
                                    time.sleep(1)
                                    self.statusBar().clearMessage()
                        except:
                            print("Error- message could not be handled!")

                elif json_body['type'] == 'login':
                        
                        arm_state = json_body['arm_state']
                        user = json_body['username']
                        access_lvl = json_body['access']
                        if arm_state == "Armed": 
                            self.state.setText("System is ARMED")
                            self.user_data.setText("")
                            self.window_state = AccessState.ARM_WINDOW
                            self.set_window_to_state()

                        else:
                            self.state.setText("")
                            self.user_data.setText("Welcome, %s!" % user)
                            #trail
                            #self.enrollWindow.instructions.setText("Welcome, %s!" % user)
                            self.window_state = AccessState.DISARM_WINDOW
                            self.set_window_to_state()

            # Now delete the ack'ed message
            for item in acked_messages:
                self.client.delete_message(QueueUrl=self.queue, ReceiptHandle=item)

        # otherwise just return
        else:
            return


 
    def pubFingerprint(self, state, uname):
        """
        Publish Fingerprint Authentication results to AWS        
        """

        armData = {}
        if uname == None:
            uname="None"
        armData['state']=str(state) 
        armData['user_id']  =str(uname) 
        jsonData = json.dumps(armData)

        print("PUB FINGERPRINT\n\tSending state:%s, user_id:%s" % (state, uname))
        self.myAWSIoTMQTTClient.publish("AccessControl/Fingerprint", str(jsonData), 1)



    def pubUserPass(self, uname, passwd):
        """
        Publish the username and password info to AWS in order to validate
        """

        if len(uname) < 5 or len(passwd) < 5:
            self.statusBar().showMessage('Username and Password must each be > 5 chars!')
            return

        unameData = {}
        unameData['user_name']=str(uname)
        unameData['password']=str(passwd)
        jsonData = json.dumps(unameData)

        print("PUB USER PASS\n\tSending user:%s, password:%s" % (uname, "*"*(len(passwd)-4)+passwd[-3:]))
        self.myAWSIoTMQTTClient.publish("AccessControl/UserPass", str(jsonData), 1)


    def pubaddFingerprint(self, name, user_id):
        """
        Publish new Fingerprint added to AWS       
        """
        usrData = {}
        if name == None:
                name="None"
        if user_id == None:
                user_id="None"
        usrData['name']=str(name) 
        usrData['user_id']  =str(user_id) 
        jsonData = json.dumps(usrData)

        print("PUB to addFINGERPRINT\n\t username:%s, user_id:%s" % (name,user_id))
        self.myAWSIoTMQTTClient.publish("AccessControl/addFingerprint", str(jsonData), 1)



    def pubrmFingerprint(self, name):
        """
        Publish new Fingerprint added to AWS       
        """
        usrData = {}
        if name == None:
                name="None"
        usrData['name']=str(name) 
        #usrData['user_id']  =str(user_id) 
        jsonData = json.dumps(usrData)

        print("PUB FINGERPRINT\n\t username:%s" % (name))
        self.myAWSIoTMQTTClient.publish("AccessControl/rmFingerprint", str(jsonData), 1)



    def initUI(self):
        """ 
        Initialize + configure all QT modules used in the GUI
        And place them on the screen in the application
        """
	
	# create QT font
        font = QtGui.QFont()
        font.setFamily(QtCore.QString.fromUtf8("FreeMono"))
        font.setBold(True)
        font.setPointSize(20)

	# Create user-name label
        self.user_data=QtGui.QLabel(self)
        self.user_data.setFont(font)
        self.user_data.setText("")

	# Create alarm-state label
        self.state=QtGui.QLabel(self)
        self.state.setFont(font)
        self.state.setText("System is ARMED")
	self.state.setStyleSheet("color: red")

        # Label for username
        self.input1Label=QtGui.QLabel(self)
        self.input1Label.setText("Username")

        # Create text input
        self.input1=QtGui.QLineEdit(self)
        #self.input1.setHint("Username")
	
        self.unamebox = QtGui.QHBoxLayout()
        self.unamebox.addWidget(self.input1Label)
        self.unamebox.addWidget(self.input1)

        # Label for username
        self.input2Label=QtGui.QLabel(self)
        self.input2Label.setText("Password")

        # Create text input
        self.input2=QtGui.QLineEdit(self)
        self.input2.setEchoMode(QtGui.QLineEdit.Password)
        #self.input2.setHint("Password")

	# Password Button
	self.Submit_btn=QtGui.QPushButton("Submit", self)
	self.Submit_btn.clicked.connect(self.sendLoggedInUser)
        
        self.passwdbox = QtGui.QHBoxLayout()
        self.passwdbox.addWidget(self.input2Label)
        self.passwdbox.addWidget(self.input2)
        self.passwdbox.addWidget(self.Submit_btn)

	# Create status bar
	self.statusBar()
	self.statusBar().setStyleSheet("color: red; font-size:18pt")

		
	# Create Disarm button        
	Disarm_btn=QtGui.QPushButton("Finger print Access",self)
        Disarm_btn.clicked.connect(self.verify)

	# Now create layout
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)

	# put buttons in an hbox
        status_box=QtGui.QVBoxLayout()
        status_box.addWidget(self.user_data)
        status_box.addWidget(self.state)

	# put buttons + status in a vbox
	vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.unamebox)
        vbox.addLayout(self.passwdbox)

        #access buttons 
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(Disarm_btn)
        hbox.addLayout(vbox)
        
        #combine widgets
        fingerprintbox = QtGui.QVBoxLayout()
        fingerprintbox.addLayout(status_box)
        fingerprintbox.addLayout(hbox)

        #set layout
	wid.setLayout(fingerprintbox)
        wid.setLayout(hbox)
        self.setGeometry(50,50,600,400)
        self.setWindowTitle('Project 2 Demo')
    


    def set_window_to_state(self):

        print ("Arm state is %d" % self.window_state)

        if self.window_state != AccessState.ARM_WINDOW:
            print("Hiding arm window")
            self.hide()

        if self.window_state != AccessState.DISARM_WINDOW and self.enrollWindow != None:
            print("Hiding disarm window")
            self.enrollWindow.teardown()
            self.enrollWindow = None

        if self.window_state == AccessState.ARM_WINDOW:
            print("Showing arm window")
            self.show()

        elif self.window_state == AccessState.DISARM_WINDOW:
            print("Showing disarm window")
            self.enrollWindow = EnrollWindow(self)
            self.enrollWindow.show()


    def verify(self):
        my_verify = verifier()
        print("Verification")
        self.statusBar().showMessage("Press your finger")
        self.verify_result = my_verify.runscript()
        if self.verify_result is None:
    		#self.pubAccessState("Armed")
        	self.statusBar().showMessage("Access Denied")
        	time.sleep(1)
        	self.statusBar().clearMessage()
        else:
    		#self.pubAccessState("Disarmed")
                self.pubFingerprint(state="Success", uname=self.verify_result)
		self.hide()
        	self.newWindow= EnrollWindow(self)
                


    def sendLoggedInUser(self):
        """
        Send (username, password) pair to AWS for authentication
        """
        uname =self.input1.text()
        passwd=self.input2.text()
        self.pubUserPass(uname, passwd)
        return



    def simFingerprintSuccess(self):
        """
        Change the state of the Arm_status table in MySQL to 'disarmed' and set current user
        """
        rand_ID = int(numpy.floor(numpy.random.uniform(0,4)))
	
        self.pubFingerprint(state="Success", uname=rand_ID)
        return



    def simFingerprintFailure(self):
        """
        Change the state of the Arm_status table in MySQL to 'disarmed'
        """
        self.pubFingerprint(state="Failure", uname=None)
        return


 
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
    access=Access()
    sys.exit(app.exec_())
