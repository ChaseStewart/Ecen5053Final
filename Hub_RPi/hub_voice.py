#!/usr/bin/env python
# Requires PyAudio and PySpeech.
 
import speech_recognition as sr
import pyaudio
import os
import time
from gtts import gTTS
import subprocess
import boto3
import urllib2
import smtplib
import requests
import time
import re
import sys
from wordsegment import segment
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QSound

class Hub_voice(QtGui.QMainWindow):
    
    def __init__(self,parent = None):

        super(Hub_voice,self).__init__(parent)
        self.speech_text = None
        self.name = None
        self.light_on = None
        self.light_of = None
        self.user_name = None
        self.logout = None
        self.count = 0
        self.parent = parent
        self.commands()

    def commands(self):
        # Record Audio
        self.speech_text = sr.Recognizer()
        while True:
            with sr.Microphone() as source:
                print("Say something!")
                self.speech_text.adjust_for_ambient_noise(source)
                print("set minimum energy threshold to {}".format(self.speech_text.energy_threshold)) 
                audio = self.speech_text.listen(source)
                print("Said something!")
        # Speech recognition using Google Speech Recognition
            try:
                Resp_Text = self.speech_text.recognize_google(audio)
                print("You said: " + Resp_Text)
                #self.name = re.search('purple',Resp_Text.lower())
                self.logout = re.search('logout',Resp_Text.lower())
                #self.light_on = re.search('lights on',Resp_Text.lower())
                #self.light_of = re.search('lights off',Resp_Text.lower())
                self.user_name = re.search('who am i',Resp_Text.lower())
                self.music = re.search('music',Resp_Text.lower())
                self.next = re.search('next',Resp_Text.lower())
                self.last = re.search('previous',Resp_Text.lower())
                self.stop = re.search('stop',Resp_Text.lower())

                if self.user_name!= None :
                # call hub function
            
                    a=self.parent.logged_in_user
                    if a != None:
                        tts = gTTS(text="Hi "+a, lang='en')
                        tts.save("good.mp3")
                        os.system("mpg321 good.mp3 &")
                        time.sleep(2)
                        
                if self.music!=None:
                    fnames = os.listdir("/media/pi/B214-AB4E/Testing")
                    print fnames[self.count]
                    path = "mpg321 -K /media/pi/B214-AB4E/Testing/"+fnames[self.count]+" &"
                    print path
                    os.system(path)
                    time.sleep(2)

                    
                if self.next!=None:
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
                
                


                    
        
##            if self.name != None :
##                tts = gTTS(text="Hello all! This is purple.Thanks for having me in T9 Hackathon...I am here to empower women.", lang='en')
##                tts.save("good.mp3")
##                os.system("mpg321 good.mp3 &")
##                time.sleep(15)
##
##            elif  self.logout!=None:
##                # call hub function
##                if a != None:
##                    tts = gTTS(text="Bye "+a, lang='en')
##                    tts.save("good.mp3")
##                    os.system("mpg321 good.mp3 &")
##                    print(a)
##                    time.sleep(15)
##
##            elif self.light_on=!= None:
##                # call hub function
##                if a != None:
##                    tts = gTTS(text="Lights turned on "+a, lang='en')
##                    tts.save("good.mp3")
##                    os.system("mpg321 good.mp3 &")
##                    time.sleep(15)
##
##            elif self.light_of!= None:
##                # call hub function
##                if a != None:
##                    tts = gTTS(text="Lights turned off "+a, lang='en')
##                    tts.save("good.mp3")
##                    os.system("mpg321 good.mp3 &")
##                    time.sleep(15)
                
              

            except :
                tts = gTTS(text="Sorry could not get you.Ask for current user name logout switch lights on or off ", lang='en')
                tts.save("good.mp3")
                os.system("mpg321 good.mp3 &")
                time.sleep(10)
                
if __name__ == "__main__":
    """ Run program if called as main function """
    app = QtGui.QApplication(sys.argv)
    voice_control=Hub_voice()

