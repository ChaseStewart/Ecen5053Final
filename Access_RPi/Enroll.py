#!/usr/bin/env python

import fingerpi as fp
import time
f = fp.FingerPi()
i=1

print 'Opening connection...'
f.Open(extra_info = True, check_baudrate = True)

print 'Change baudrate'
f.ChangeBaudrate(115200)
f.CmosLed(True)


response = f.GetEnrollCount()
if response[0]['ACK']:
    i=response[0]['Parameter']
    i=i+1
    print  i
while True:
    print 'start enrolling'
    response = f.EnrollStart(i)
    if response[0]['ACK']:
        break
    else:
        print 'error',response[0]['Parameter']
print 'Place the finger on the scanner'
while True:
    print 'IspressFinger'
    response = f.IsPressFinger()
    if response[0]['ACK']:
        if response[0]['Parameter']==0:
            time.sleep(3)
            break    
while True:
    print 'captureFinger'
    response = f.CaptureFinger()
    if response[0]['ACK']:
        break
    else:
        print 'error',response[0]['Parameter']
print 'Remove Finger'
while True:
    print 'Enrollment 1'
    response = f.Enroll1()
    if response[0]['ACK']:
        break
    else:
        print 'error',response[0]['Parameter']
        break
while True:
    print 'IspressFinger'
    response = f.IsPressFinger()
    if response[0]['ACK']:
        if response[0]['Parameter']==0:
            print 'Remove the finger'
        else:
            time.sleep(3)
            break
print 'Place the finger on the scanner'
while True:
    print 'IspressFinger'
    response = f.IsPressFinger()
    if response[0]['ACK']:
        if response[0]['Parameter']==0:
            time.sleep(3)
            break
while True:
    response = f.CaptureFinger()
    if response[0]['ACK']:
        break
    else:
        print 'error',response[0]['Parameter']
print 'Remove your finger'
while True:
    print 'Enrollment 2'
    response = f.Enroll2()
    if response[0]['ACK']:
        break
    else:
        print 'error',response[0]['Parameter']
        break
while True:
    print 'IspressFinger'
    response = f.IsPressFinger()
    if response[0]['Parameter']==0:
        print 'Remove the finger'
    else:
        time.sleep(3)
        break
print 'Place the finger on the scanner'
while True:
    print 'IspressFinger'
    response = f.IsPressFinger()
    if response[0]['ACK']:
        if response[0]['Parameter']==0:
            time.sleep(3)
            break
while True:
    response = f.CaptureFinger()
    if response[0]['ACK']:
        break
    else:
        print 'error',response[0]['Parameter']
        break
print 'Remove finger'
while True:
    print 'Enrollment 3'
    response = f.Enroll3()
    if response[0]['ACK']:
        print 'registration completed'
        break
    else:
        print 'error',response[0]['Parameter']
        break
f.CmosLed(False)   
print 'Closing connection...'
f.Close()
