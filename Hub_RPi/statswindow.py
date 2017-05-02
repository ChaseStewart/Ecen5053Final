#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys, json, numpy
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from helpers import WindowState
import numpy as np

# MatPlotLib setup
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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
		self.axes.plot(range(10), [np.nan]*10,'r')
		self.axes.set_xlabel('Time')
		self.axes.set_ylabel('Lights ON ', color='r')
		self.axes.set_ylim(0,1)
		self.axes.set_title('Usage of Lights ')
		
		# set up blue plot
		self.ax2 = self.axes.twinx()
		self.ax2.plot(range(10), [np.nan]*10, 'b')
		self.ax2.set_ylabel('Lights Off', color='b')
		self.ax2.set_ylim(0,1)


	def update_figure(self, humData, tempData):
		"""
		Update the line chart w/ data from the caller
		"""

		# need to clear axes to place new data
		self.axes.cla()
		self.ax2.cla()

		# unfortunately this means replacing limits and labels w/ data
		self.axes.set_ylim(0,1)
		self.axes.plot(range(10),lights_on,'r')
		self.axes.set_ylabel('Lights ON ', color='r')
		self.axes.set_title('Usage of Lights ')
		
		# same goes for humidity data
		self.ax2.set_ylim(0,1)
		self.ax2.plot(range(10), lights_of, 'b')
		self.ax2.set_ylabel('Lights Off', color='b')
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
        self.red = None
        self.blue = None
        self.green = None
        self.lights_on = None
        self.lights_of = None
        self.initUI()


    def initUI(self):

	# create QT font
        self.font = QtGui.QFont()
        self.font.setFamily(QtCore.QString.fromUtf8("Helvetica"))
        self.font.setBold(True)
        self.font.setPointSize(20)

        # init timer
	self.timer = QTimer()
	self.timer.timeout.connect(self.printStats)
	self.timer.stop()
	
	# button to set automatic data capture
	self.autostart = QtGui.QPushButton('Start', self)
	self.autostart.setToolTip('Click to start auto measurement')
	self.autostart.clicked.connect(self.timerStart)

	# Create user-name label
        self.stats=QtGui.QLabel(self)
        self.stats.setFont(self.font)
        self.stats.setText("System Stats")
        
        
        # put buttons + status in a vbox
        self.goback=QtGui.QPushButton("Back",self)
        self.goback.clicked.connect(self.goBack)

        self.canvas = DynamicGraph(self, width=2.5, height=2.5, dpi=50)

	

        wid = QtGui.QWidget(self)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.autostart)
        hbox.addWidget(self.goback)
	vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.stats)
        vbox.addWidget(self.canvas)
        vbox.addLayout(hbox)
	wid.setLayout(vbox)
        self.setCentralWidget(wid)

        # set to armed
        self.setGeometry(50,50,600,400)
        self.setWindowTitle('System Stats')



    def printStats(self):

        self.red = self.parent.red
        self.green = self.parent.green
        self.blue = self.parent.blue
        if self.red !=0 or self.blue != 0  or self.green !=0:
            lights_on = 1
            lights_of = 0
        else:
            lights_of = 1
            lights_on = 0
        return

    def timerStart(self):
		"""
		Start the timer
		"""	
		self.timer.start(100000)
		return


    def goBack(self):
        self.parent.window_state = WindowState.MAIN_WINDOW
        self.parent.set_window_to_state()



    def teardown(self):
        self.close()

