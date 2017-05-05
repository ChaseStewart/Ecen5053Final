#!/usr/bin/env python
# Requires PyAudio and PySpeech.
 
import speech_recognition as sr
import pyaudio
import os, re, sys, json
import time
from gtts import gTTS
import subprocess
import boto3
import urllib2
import smtplib
import requests
from wordsegment import segment
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QSound

from helpers import VoiceState

class Hub_voice(QtGui.QMainWindow):

    """
      Detects the default device and uses Goople Voice API
    """
    

    def __init__(self,parent = None):

        """
        start listeneing
        """
    
        super(Hub_voice,self).__init__(parent)

        #var for the words it is searching for
        self.speech_text = None
        self.name     = None
        self.light_on = None
        self.light_of = None
        self.user_name = None
	self.light_blue  = None
	self.light_red   = None
	self.light_green = None

        self.stop_listening = None
        self.logout = None
        self.count = 0
        self.parent = parent
	self.IS_RUNNING = VoiceState.RUNNING

    def listen_once(self):

        """
        select default input and record
        """
        # Record Audio
        try:
            self.speech_text = sr.Recognizer()
            with sr.Microphone() as source:
                self.speech_text.adjust_for_ambient_noise(source)
                print("set minimum energy threshold to {}".format(self.speech_text.energy_threshold)) 

                print("Say something!")
                audio = self.speech_text.listen(source)
                print("Said something!")
                self.process_voice(audio)

        #when no mic is attached
        except Exception as e:
            print e
            self.IS_RUNNING = VoiceState.ERROR
            

		
    def process_voice(self, audio):

            """
            Process the audio recorded and send commands
            """
            
            # Speech recognition using Google Speech Recognition
            try:
                Resp_Text = self.speech_text.recognize_google(audio)
                print("You said: " + Resp_Text)

		# LED commands
                self.light_red     = re.search('lights red',  Resp_Text.lower())
                self.light_blue    = re.search('lights blue', Resp_Text.lower())
                self.light_green   = re.search('lights green',Resp_Text.lower())
                self.light_green_2 = re.search('white screen',Resp_Text.lower())

		# control commands
                self.end_voice   = re.search('end voice', Resp_Text.lower())
 		self.end_voice_2 = re.search('invoice',   Resp_Text.lower())
                self.logout      = re.search('logout',    Resp_Text.lower())
                self.user_name   = re.search('who am i',  Resp_Text.lower())
 
		# music commands
                self.music = re.search('music',   Resp_Text.lower())
                self.next = re.search('next',     Resp_Text.lower())
                self.last = re.search('previous', Resp_Text.lower())
                self.stop = re.search('stop',     Resp_Text.lower())

                if self.user_name!= None :
                    
                    # call hub function
                    a=self.parent.logged_in_user
                    if a != None:
                        tts = gTTS(text="Hi "+a, lang='en')
                        tts.save("good.mp3")
                        os.system("mpg321 good.mp3 &")
                        time.sleep(2)

		if self.light_red != None:
                    
		    jsonData = {}
		    jsonData['type']  = 'led'
		    jsonData['blue']  = 0
		    jsonData['red']   = 255
		    jsonData['green'] = 0
		    strData = json.dumps(jsonData)
                    
                    self.parent.myAWSIoTMQTTClient.publish("AccessControl/set_leds", strData, 1)
                    print("Published red")	
                    time.sleep(0.1)	
	
                if self.light_blue != None:
                    
		    jsonData = {}
		    jsonData['type']  = 'led'
		    jsonData['blue']  = 255
		    jsonData['red']   = 0
		    jsonData['green'] = 0
		    strData = json.dumps(jsonData)
                    
                    self.parent.myAWSIoTMQTTClient.publish("AccessControl/set_leds", strData, 1)
                    print("Published blue")
                    time.sleep(0.1)	
		
                if self.light_green != None or self.light_green_2 != None:
                    
		    jsonData = {}
		    jsonData['type']  = 'led'
		    jsonData['blue']  = 0
		    jsonData['red']   = 0
		    jsonData['green'] = 255
		    strData = json.dumps(jsonData)
                    
                    self.parent.myAWSIoTMQTTClient.publish("AccessControl/set_leds", strData, 1)
                    print("Published green")	
                    time.sleep(0.1)	
                        
                if self.music != None:
                    
                    fnames = os.listdir("/media/pi/B214-AB4E/Testing")
                    print fnames[self.count]
                    path = "mpg321 -K /media/pi/B214-AB4E/Testing/"+fnames[self.count]+" &"
                    print path
                    os.system(path)
                    time.sleep(2)

                    
                if self.next != None:
                    fnames = os.listdir("/media/pi/B214-AB4E/Testing")
                    self.count=self.count+1
                    if self.count < 20 :
                        print fnames[self.count]
                        path = "mpg321 -K /media/pi/B214-AB4E/Testing/"+fnames[self.count]+" &"
                        print path
                        os.system("pkill mpg321")
                        os.system(path)
                        time.sleep(2)
                    else:
                        self.count = 0

                if self.last!=None:
                    fnames = os.listdir("/media/pi/B214-AB4E/Testing")
                    self.count=self.count-1
                    if self.count > 0 :
                        print fnames[self.count]
                        path = "mpg321 -K /media/pi/B214-AB4E/Testing/"+fnames[self.count]+" &"
                        print path
                        os.system("pkill mpg321")
                        os.system(path)
                        time.sleep(2)
                    else:
                        self.count = 0

                if self.stop!=None:
                    os.system("pkill mpg321")

                if self.logout!= None :
                    a=self.parent.setLogoutPage()
                    if a != None:
                        tts = gTTS(text="Logged out successfully", lang='en')
                        tts.save("good.mp3")
                        os.system("mpg321 good.mp3 &")
                        time.sleep(2)

		if self.end_voice != None or self.end_voice_2 != None:
                    print("Stopping Voice\n")
                    self.IS_RUNNING = VoiceState.STOP

            except Exception as e:
		print e
                tts = gTTS(text="Sorry could not get you.Ask for current user name logout switch lights on or off ", lang='en')
                tts.save("good.mp3")
                os.system("mpg321 good.mp3 &")
                time.sleep(10)
	
                
if __name__ == "__main__":
    
    """ Run program if called as main function """
    app = QtGui.QApplication(sys.argv)
    voice_control=Hub_voice()

