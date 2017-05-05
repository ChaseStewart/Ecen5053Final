#!/usr/bin/env python

import fingerpi as fp
import time


class verifier:
    """
        Check if finger pressed is enrolled

    """

    def __init__(self):
        pass
    
    def runscript(self):

        """
        capture finger print and returns a success or failure
        """
        
        f=fp.FingerPi()
        
        print 'Opening Connection...'
        f.Open(extra_info=True,check_baudrate = True)
        f.CmosLed(True)
        print 'Verifying Place the finger on the scanner'

        #checks if finger is pressed
        while True:
            print 'IspressFinger'
            response = f.IsPressFinger()
            if response[0]['ACK']:
                if response[0]['Parameter']==0:
                    time.sleep(3)
                    break

        #sends the command capture finger
        while True:
            response = f.CaptureFinger()
            if response[0]['ACK']:
                break
            else:
                print 'error',response[0]['Parameter']
                break
        print 'Fingerprint scanned'

        #checks if fingerprint is enrolled
        response=f.Identify()
        if response[0]['ACK']:
            print 'ID is',response[0]['Parameter']
        else:
            print 'Register now! not registered'
            return None
        
        f.CmosLed(False)
        f.Close()
        print 'Closing Connection'
        return response[0]['Parameter']
