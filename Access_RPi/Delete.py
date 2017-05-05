#!/usr/bin/env python

import fingerpi as fp
import time


class Deleting:
    """
        To delete fingerprint by ID
    """
    
    def __init__(self):
        pass

    def runscript(self,ID):
        """
        Deletes fingerprint by ID
        """
        
        f = fp.FingerPi()
        print 'Opening connection...'
        f.Open(extra_info = True, check_baudrate = True)

        #sends messsage to UART
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

