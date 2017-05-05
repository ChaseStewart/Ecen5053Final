#!/usr/bin/env python

import fingerpi as fp
import time

"""
Delete all records from the fingerprint sensor- helpful for debug
"""


f = fp.FingerPi()
print 'Opening connection...'

# open a serial connection to the fingerprint sensor
f.Open(extra_info = True, check_baudrate = True)

# now call deleteAll- try again and again if it fails 
while True:
    print 'Deleting all previous id'
    response = f.DeleteAll()
    if response[0]['ACK']:
        break
    else:
        print 'error',response[0]['Parameter']
    
        
    print 'closing connection'
    f.Close()

