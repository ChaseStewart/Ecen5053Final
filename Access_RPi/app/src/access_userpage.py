#!/usr/bin/python

"""userpage.py: this is Chase Stewart's implementation of the ECEN 5053-003 superproject user page """

__author__    = "Chase E. Stewart"
__copyright__ = "I think LGPL "



# import general libraries
import sys
import Adafruit_DHT
from time import time, gmtime, strftime, sleep
import numpy as np
import MySQLdb

# import PyQT
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QRadioButton, QLabel, QSizePolicy, QHBoxLayout, QVBoxLayout 
from PyQt5.QtGui import QIcon 
from PyQt5.QtCore import pyqtSlot, QTimer



class App(QWidget):
	"""
	This main class controls everything to do with the display
	"""

	def __init__(self):
		"""
		Initialize the superclass and class vars
		"""
		super(QWidget, self).__init__()
		self.title  = 'User Page'
		self.left   = 100
		self.top    = 100
		self.width  = 750
		self.height = 430

		# results of mysql query
		self.resultslist = []

		# set time for auto measurement
		self.deltaTime=1000

		self.host   = "52.34.209.113"
		self.user   = "rpi"
		self.passwd = "mounika"


		self.initialize()

	def initialize(self):
		"""
		Create the buttons and link callbacks
		"""

		# set window basic info
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		# init timer
		self.timer = QTimer()
		self.timer.timeout.connect(self.autoUpdate)
		self.timer.stop()
		
		# button to just get data		
		self.update = QPushButton('Get Data', self)
		self.update.setToolTip('Push to get sensor data')
		self.update.clicked.connect(self.queryMySQL)

		# button to set automatic data capture
		self.autostart = QPushButton('AutoStart', self)
		self.autostart.setToolTip('Click to start auto measurement')
		self.autostart.clicked.connect(self.timerStart)
		
		# button to stop automatic data capture
		self.autostop = QPushButton('AutoStop', self)
		self.autostop.setToolTip('Click to stop auto measurement')
		self.autostop.clicked.connect(self.timerStop)
		
		# start and stop buttons
		self.startNStop = QHBoxLayout()
		self.startNStop.addWidget(self.autostart)
		self.startNStop.addWidget(self.autostop)

		# text input for data
		self.periodInput = QLineEdit(self)
		self.periodInput.setToolTip('Enter Frequency of auto measurement')
		self.periodInput.setMaxLength(5)

		# text input for period
		self.period = QLabel(self)
		self.period.setText('Period (msec)')
		
		# freq input
		self.periodInputLayout = QHBoxLayout()
		self.periodInputLayout.addWidget(self.periodInput)
		self.periodInputLayout.addWidget(self.period)
		
		# label for freq setting
		self.periodLabel = QLabel(self)
		self.periodLabel.setText('Set automatic data period')
		
		# label for freq setting
		self.currPeriod = QLabel(self)
		self.currPeriod.setText('Period: %s ms' % self.deltaTime)
		self.currPeriod.setStyleSheet('font: italic')
	
		# label for period
		self.periodNAlert = QHBoxLayout()
		self.periodNAlert.addWidget(self.periodLabel)
		self.periodNAlert.addWidget(self.currPeriod)
	
		# label for user_data DB info
		self.sensorLabel = QLabel(self)
		self.sensorLabel.setStyleSheet('font: bold')
		self.sensorLabel.setText('Database information will be here')

		# label for alerts
		self.alerts = QLabel(self)
		self.alerts.setText('No alerts')
		self.alerts.setStyleSheet('color: red')
		#self.alerts.hide()

		# input buttons
		self.inputBox = QVBoxLayout()
		self.inputBox.addLayout(self.periodNAlert)
		self.inputBox.addLayout(self.periodInputLayout)
		self.inputBox.addLayout(self.startNStop)

		# alert and update buttons
		self.alertNUpdate = QHBoxLayout()
		self.alertNUpdate.addWidget(self.alerts)
		self.alertNUpdate.addWidget(self.update)

		# set overarching VBox
		self.vert1 = QVBoxLayout()
		self.vert1.addWidget(self.sensorLabel)
		self.vert1.addLayout(self.alertNUpdate)
		self.vert1.addLayout(self.inputBox)

		self.setLayout(self.vert1)
		self.show()


	def getMySQLData(self):
		"""
		Use Adafruit lib to get and convert sensor reading
		"""
		self.resultslist = []

		db = MySQLdb.connect(host=self.host, port=3306, user=self.user, passwd=self.passwd)
		c = db.cursor()
		c.execute("""SELECT name, email FROM users_data.users_data;""")
		
		for item in c:
			self.resultslist.append(item)

		return


	
	def timerStart(self):
		"""
		Start the timer
		"""
		
		# check for valid delta time
		try:
			self.deltaTime = int(self.periodInput.text())

		# or else set back to default time
		except:
			self.alerts.setText('Invalid period - defaulting to 1 second')
			self.deltaTime = 1000		

		print("Delta Time is "+str(self.deltaTime))
		self.currPeriod.setText('Period: %s ms' % self.deltaTime)
		self.timer.start(self.deltaTime)
		return



	def timerStop(self):
		"""
		Stop the timer
		"""
		self.timer.stop()
		return



	@pyqtSlot()
	def queryMySQL(self):
		"""
		Query the DB
		"""

		self.getMySQLData()

		tempstring = ""
		for item in self.resultslist:
			tempstring += "Name: "+ item[0] +" Email: "+item[1]+"\r\n"
		
		self.sensorLabel.setText(tempstring)

	def autoUpdate(self):
		"""
		Automatically gather data
		"""
		
		self.queryMySQL()
		return



if __name__ == '__main__':
	"""
	Start the application
	"""

	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())

