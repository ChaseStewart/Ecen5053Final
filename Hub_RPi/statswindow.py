#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys, json, numpy
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from helpers import WindowState
from helpers import GraphState
from time import time
import numpy as np

# MatPlotLib setup
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# protocol testing libraries
import paho.mqtt.publish as publish
import websocket
from coapthon.client.helperclient import HelperClient

class graphCanvas(FigureCanvas):
	"""
	This class is a generic FigureCanvas class
	"""

	def __init__(self, parent=None, width=2.5, height=2.5, dpi=80):
		"""
		The formal initialization of the FigureCanvas class and canvas
		"""
	
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = fig.add_subplot(111)
		self.compute_initial_figure()

		FigureCanvas.__init__(self, fig)

		self.setParent(parent)

		FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

	def compute_initial_figure(self):
		"""
		A stand-in for the other class's init graph routine
		"""
		pass

	    
class DynamicGraph(graphCanvas):
	"""
	This class actually holds the graph 
	"""

	def __init__(self, *args, **kwargs):
		"""
		Does a superclass init to graphCanvas
		"""
		graphCanvas.__init__(self, *args, **kwargs)

	def compute_initial_figure(self):
		"""
		renders the plot before any data has been taken
		"""
		
		# set up red plot
		self.ax2 = self.axes.twinx()
		self.ax3 = self.axes.twinx()
		self.ax4 = self.axes.twinx()
		
		self.ax3.plot(range(10), [np.NaN]*10,'r', label='dummy1')
		self.axes.set_ylabel('axis 1', color='r')
		self.axes.set_ylim(-1,2)

		self.axes.set_xlabel('Sample')
		self.axes.set_title('Choose a stat to graph')
		
		# set up blue plot
		
		self.ax2.plot(range(10), [np.NaN]*10, 'b', label='dummy2')
		self.ax2.set_ylabel('axis 2', color='b')
		self.ax2.set_ylim(-1,2)
                self.ax2.get_yaxis().set_ticks([])

		self.ax3.set_ylim(-1,2)
                self.ax3.get_yaxis().set_ticks([])

		self.ax4.set_ylim(-1,2)
                self.ax4.get_yaxis().set_ticks([])


	def update_figure(self, graph_type, led1array, led2array, array3=None ):
		"""
		Update the line chart w/ data from the caller
		"""

		# need to clear axes to place new data
		self.axes.cla()
		self.ax2.cla()
		self.ax3.cla()
		self.ax4.cla()


		if graph_type == GraphState.LIGHTS:
                        
                        self.axes.set_ylabel('Lights ON ', color='r')
                        self.axes.set_title('Usage of Lights ')
                        self.axes.set_ylim(-1,2)

                        self.ax2.set_ylabel('Lights Off', color='b')
                        self.ax2.plot(range(10), led2array, 'b', label="Lights Off")
                        self.ax2.set_ylim(-1,2)
                        self.ax2.get_yaxis().set_ticks([])

                        self.ax3.plot(range(10),led1array,'r', label="Lights On")
                        self.ax3.set_ylim(-1,2)
                        self.ax3.get_yaxis().set_ticks([])
                        
                        self.ax4.set_ylim(-1,2)
                        self.ax4.get_yaxis().set_ticks([])

			self.legend = self.axes.legend(loc='center', shadow=True)	

                if graph_type == GraphState.RGB:
                        
                        self.axes.set_ylabel('Value (0-255) ', color='k')
                        self.axes.set_title('Color on LEDs ')
                        self.axes.set_ylim(0,256)

                        self.ax2.plot(range(10), led2array, 'b', label="Blue")
                        self.ax2.set_ylim(0,256)
                        self.ax2.get_yaxis().set_ticks([])

                        self.ax3.plot(range(10),led1array,'r', label="Red")
                        self.ax3.set_ylim(0,256)
                        self.ax3.get_yaxis().set_ticks([])
		
                        self.ax4.plot(range(10), array3, 'g', label="Green")
                        self.ax4.set_ylim(0,256)
                        self.ax4.get_yaxis().set_ticks([])
			
			self.legend = self.axes.legend(loc='center', shadow=True)	
                        
                if graph_type == GraphState.LATENCY:
                        
                        self.axes.set_title('Latency for all protocols ')
                        self.axes.set_ylabel('Latency', color='k')
			self.axes.set_ylim(0,1)
                        
                        self.ax2.plot(range(10), led2array, 'b', label="CoAP")
			self.ax2.set_ylim(0,1)
                        self.ax2.get_yaxis().set_ticks([])

                        self.ax3.plot(range(10),led1array,'r', label="WS")
			self.ax3.set_ylim(0,1)
                        self.ax3.get_yaxis().set_ticks([])

                        self.ax4.plot(range(10), array3, 'g', label="MQTT")
			self.ax4.set_ylim(0,1)
                        self.ax4.get_yaxis().set_ticks([])
			
			self.legend = self.axes.legend(loc='center', shadow=True)	

                self.draw()


class StatsWindow(QtGui.QMainWindow):
    """
    This is the window that should be shown when the device is locked
    """

    def __init__(self, parent=None):
        """
        initialize this window
        """
	super(StatsWindow, self).__init__(parent)

        self.parent = parent

        self.red   = 0
        self.blue  = 0
        self.green = 0
        
        self.lights_on  = 0
        self.lights_of  = 0
        self.graph_type = None
        
        # Light on arrays
	self.led1array    = [np.NaN]*10
	self.led2array    = [np.NaN]*10
	self.array3       = [np.NaN]*10
	self.plotCount = 0

	# Proto Latency arrays
        self.wsArray   = [np.NaN] * 10 
	self.mqttArray = [np.NaN] * 10
	self.coapArray = [np.NaN] * 10
	self.latencyCount = 0

	# RGB arrays
        self.redArray   = [np.NaN] * 10 
	self.blueArray  = [np.NaN] * 10
	self.greenArray = [np.NaN] * 10
	self.rgbCount = 0
        
	self.initUI()



    def initUI(self):

	# create QT font
        self.font = QtGui.QFont()
        self.font.setFamily(QtCore.QString.fromUtf8("Helvetica"))
        self.font.setBold(True)
        self.font.setPointSize(20)

        # init timer
	self.timer = QTimer()
	self.timer.stop()
	
	# button for lights on
	self.lights = QtGui.QPushButton('Lights', self)
	self.lights.setToolTip('Click to get status of lights in rooms')
	self.lights.clicked.connect(self.ledTimerStart)

	# button for overhead
        self.overhead = QtGui.QPushButton('RGB', self)
	self.overhead.setToolTip('Click to graph the red, green, blue displayed in the LEDs')
	self.overhead.clicked.connect(self.RGBTimerStart)

	# button for latency
        self.latency = QtGui.QPushButton('Latency', self)
	self.latency.setToolTip('Click to find the latency for protocols')
	self.latency.clicked.connect(self.latencyTimerStart)

	# Create user-name label
        self.stats=QtGui.QLabel(self)
        self.stats.setFont(self.font)
        self.stats.setText("System Stats")
        
        # put buttons + status in a vbox
        self.goback=QtGui.QPushButton("Back",self)
        self.goback.clicked.connect(self.goBack)

        self.canvas = DynamicGraph(self, width=2.5, height=2.5, dpi=50)

	

        wid = QtGui.QWidget(self)
        btn_box = QtGui.QHBoxLayout()
        btn_box.addWidget(self.lights)
        btn_box.addWidget(self.overhead)
        btn_box.addWidget(self.latency)
        btn_box.addWidget(self.goback)
	vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.stats)
        vbox.addWidget(self.canvas)
        vbox.addLayout(btn_box)
	wid.setLayout(vbox)
        self.setCentralWidget(wid)

        # set to armed
        self.setGeometry(50,50,600,400)
        self.setWindowTitle('System Stats')



    def ledStats(self):

        #vars to get the RGB values from parent
        self.red = self.parent.red
        self.green = self.parent.green
        self.blue = self.parent.blue
        
        if self.red !=0 or self.blue != 0  or self.green !=0:
                self.lights_on = 1
                self.lights_of = 0
            
        else:
                self.lights_of = 1
                self.lights_on = 0

	# When count < len(graph), just populate graph
	if self.plotCount < 10:
                self.led1array[self.plotCount] = self.lights_on
		self.led2array[self.plotCount] = self.lights_of
		self.plotCount += 1	
			
	# then keep rolling the chart over
	else:
                self.led1array[0] = self.lights_on
		self.led1array = np.roll(self.led1array, len(self.led1array)-1)		
		self.led2array[0] = self.lights_of
		self.led2array = np.roll(self.led2array, len(self.led2array)-1)

	self.canvas.update_figure(GraphState.LIGHTS, self.led1array, self.led2array)


    def latencyStats(self, mqtt, coap, ws):
	
	# When count < len(graph), just populate graph
	if self.latencyCount < 10:
                self.wsArray[self.latencyCount]   = ws
		self.mqttArray[self.latencyCount] = mqtt
		self.coapArray[self.latencyCount] = coap
		self.latencyCount += 1	
			
	# then keep rolling the chart over
	else:
                self.wsArray[0] = ws
		self.wsArray = np.roll(self.wsArray, len(self.wsArray)-1)		

		self.coapArray[0] = coap
		self.coapArray = np.roll(self.coapArray, len(self.coapArray)-1)
		
                self.mqttArray[0] = mqtt
		self.mqttArray = np.roll(self.mqttArray, len(self.mqttArray)-1)
        
	self.canvas.update_figure(GraphState.LATENCY, self.wsArray, self.coapArray, self.mqttArray)
        return



    def RGBStats(self):
        
	#vars to get the RGB values from parent
        self.red   = self.parent.red
        self.green = self.parent.green
        self.blue  = self.parent.blue
        
	# When count < len(graph), just populate graph
	if self.rgbCount < 10:
                self.redArray[self.rgbCount]   = self.red
		self.blueArray[self.rgbCount]  = self.blue
		self.greenArray[self.rgbCount] = self.green
		self.rgbCount += 1	
			
	# then keep rolling the chart over
	else:
                self.redArray[0] = self.red
		self.redArray = np.roll(self.redArray, len(self.redArray)-1)		
                self.blueArray[0] = self.blue
		self.blueArray = np.roll(self.blueArray, len(self.blueArray)-1)		
                self.greenArray[0] = self.green
		self.greenArray = np.roll(self.greenArray, len(self.greenArray)-1)		

	self.canvas.update_figure(GraphState.RGB, self.redArray, self.blueArray, self.greenArray)
        return



    def RGBTimerStart(self):
	"""
	Start the timer with timeout set to latency calculation
	"""	
	self.timer.stop()
        self.timer =  QTimer()
       	self.timer.timeout.connect(self.RGBStats)
	self.timer.start(500)
        return


    def latencyTimerStart(self):
	"""
	Start the timer with timeout set to latency calculation
	"""	
	self.timer.stop()
	self.timer =  QTimer()
       	self.timer.timeout.connect(self.startTests)
	self.timer.start(1500)
        return


    def ledTimerStart(self):
	"""
	Start the timer with timeout set to grab light setting
	"""	
	self.timer.stop()
	self.timer =  QTimer(self)
       	self.timer.timeout.connect(self.ledStats)
	self.timer.start(500)
        return


    def startTests(self):

        self.testMQTT()
        self.testWebsockets()
        self.testCoAP()
	print "tests complete!"
        return


    def testCoAP(self):
        host = '52.34.209.113'
        port = 5683
        path = 'test'
        client = HelperClient(server=(host, port))
        curr_time = time()
	try:
        	response = client.put(path, str(curr_time), timeout=0.1)
	except Exception as e:
		pass # expected because we will not receive a response from the listener
        client.stop()



    def testMQTT(self):
        curr_time = time()
        publish.single("AccessControl/MQTT_test", str(curr_time), hostname="test.mosquitto.org") 



    def testWebsockets(self):
        ws = websocket.create_connection("ws://52.34.209.113:8000")
        curr_time = time()
	ws.send(str(curr_time))



    def goBack(self):
        self.parent.window_state = WindowState.MAIN_WINDOW
        self.parent.set_window_to_state()



    def teardown(self):
        self.timer.stop()
        self.close()

