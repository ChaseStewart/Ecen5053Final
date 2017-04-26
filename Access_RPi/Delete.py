#!/usr/bin/env python

import fingerpi as fp
import time


class Deleting:
    
    def __init__(self):
        pass
    def runscript(self,ID):
        f = fp.FingerPi()
        print 'Opening connection...'
        f.Open(extra_info = True, check_baudrate = True)

        while True:
            print 'Deleting ID'
            response = f.DeleteId(ID)
            if response[0]['ACK']:
                break
            else:
                print 'error',response[0]['Parameter']
                return None
        
        print 'closing connection'
        f.Close()
        return response[0]['ACK']

