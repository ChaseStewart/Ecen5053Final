#!/usr/bin/env python

import fingerpi as fp
import time

def printByteArray(arr):
    return map(hex, list(arr))


f = fp.FingerPi()

print 'Opening connection...'
f.Open(extra_info = True, check_baudrate = True)

while True:
    print 'Deleting all previous id'
    response = f.DeleteAll()
    if response[0]['ACK']:
        break
    else:
        print 'error',response[0]['Parameter']

print 'closing connection'
f.Close()

