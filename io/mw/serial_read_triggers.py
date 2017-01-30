#!/usr/bin/python
# -*- coding: utf-8 -*-

from serial import Serial
import sys
import time
import os
from datetime import datetime
import random
import sys
import time
import signal

import thread, time

def input_thread(L):
    raw_input()
    L.append(None)
    

# MW for server side conduit:
sys.path.append('/Library/Application Support/MWorks/Scripting/Python')
from mworks.conduit import IPCClientConduit
# conduit = None
# reading = 0

def cbRespond(event):
    global conduit
    enterT = time.clock()

    if event.data == 'ping':
        conduit.send_data(conduit.reverse_codec['messageVar'], 'response')

        print 'Elapsed in cbRespond: %5.3f ms' \
            % (1000*(time.clock() - enterT))
        sys.stdout.flush()


def send_pyresponse(event):
    global conduit
    global queued
    enterT = time.clock()

    # if event.data == 'ping':
    #     print "pinged"
    #     conduit.send_data(conduit.reverse_codec['pyresponse'], 'ready')
    if event.value == "start":
        print "started"
        conduit.send_data(conduit.reverse_codec['pyresponse'], "reading")
        #signal.pause()
        queued = 1
    elif event.value == "notrunning":
        print "not running"
        queued = 0

    sys.stdout.flush()


def check_mw_display(event):
    global reading
    #global conduit
    #enterT = time.clock()
    if event.data == 1:
        #conduit.send_data(conduit.reverse_codec['messageVar'], 'response')
        #print 'Starting, time is %5.3f' % time.clock()
        reading = 1

    elif event.data == 0:
        #print 'MW display is not running'
        reading = 0

    sys.stdout.flush()


def handle_state_mode(event):
    global stopflag
    stopflag.append(event.value)
    return stopflag

def flushBuffer():
    #Flush out Teensy's serial buffer
    global ser
    tmp=0;
    while tmp is not '':
        tmp=ser.read()


# --------------------------------------------------------------
# ARDUINO STUFF:
# ---------------------------------------------------------------
#port = "/dev/ttyACM0"
port = "/dev/cu.usbmodem1411"
baudrate = 115200

print "# Please specify a port and a baudrate"
print "# using hard coded defaults " + port + " " + str(baudrate)
ser = Serial(port, baudrate, timeout=0.5)
time.sleep(1)

flushBuffer()
sys.stdout.flush()

print "Connected serial port..."


# enforce a reset before we really start
#ser.setDTR(1)
#time.sleep(0.25)
#ser.setDTR(0)

# ser.is_open()
# flushBuffer()
# sys.stdout.flush()


# --------------------------------------------------------------
# MW STUFF:
# ---------------------------------------------------------------
# if len(sys.argv) > 1:
#     # Client-side conduit: resource name is a script argument
#     resource_name = sys.argv[1]
# else:
#     # Server-side conduit: resource name is set in the experiment
resource_name = 'server_conduit'
global conduit
global queued
global reading
global stopflag

conduit = IPCClientConduit(resource_name)
conduit.initialize()

#reading = 0
#queued = 0
reading = 0
queued = 0
stopflag = []


conduit.register_callback_for_name('pyresponse', send_pyresponse)
conduit.register_callback_for_name('displaying', check_mw_display)
#time.sleep(.005)
conduit.register_callback_for_name('stop_it', handle_state_mode)

#try:
#while doing_stuff==1:
"Connected to MW..."
print "Queued: ", queued
print "Displaying: ", reading

fidx = 0

#rawfile = open(os.path.join('/tmp', 'raw.txt'), 'w')
pyserial_dir = '/Users/julianarhee/Documents/MWorks/PyData'
if not os.path.exists(pyserial_dir):
    os.makedirs(pyserial_dir)

#rawfile = open(os.path.join(pyserial_dir, 'raw%02d.txt' % fidx), 'w')
fname = sys.argv[1]
rawfile = open(os.path.join(pyserial_dir, fname+'.txt'), 'w')


print "Opened file %s.txt for write..." % fname


print "STARTING"
#ser.write('S')#TRIGGER
print "GOT CALL FROM MW"
print "Queued: ", queued

#queued = 1

nt = 0
strt = time.time()
while queued == 0:
    if (nt % 1E6) == 0:
        print "Waiting for MW. Time elapsed: %5.3f s" % (time.time()-strt)
    nt += 1

ser.write('S')#TRIGGER
# print "GOT CALL FROM MW"
# print "Queued: ", queued


#N = 0
#time.sleep(0.005)
# getout=0
# prev_ts = 0

# nt = 0
# prev_nt = 0

# ncycles = 100
# nbytes = 8

#strt = time.time()
# while getout==0:
while not (1 in stopflag):
    #if reading==1:

    curr_bts = ser.read(2000)
    rawfile.write(curr_bts)

    #nt += 1
    print curr_bts

    # if time.time() - strt >= (110*1.):
    #     getout=1
    # if queued==0:
    #     user_input = raw_input("Nothing queued. Open new file [1] or keep going []?")
    #     if user_input==1:

    #         rawfile.close()
    #         print "closed file"
    #         fidx += 1
    #         rawfile = open(os.path.join('/Users/julianarhee/Documents/MWorks/PyData', 'raw%02d.txt' % fidx), 'w')

    #     else:
    #         pass
ser.write('_*_')
time.sleep(1.0)
ser.write('F') # stop reading / sending to serial port
bytes_left = ser.inWaiting()
#while True: # Get any remaining stuff
    #bytes_left = ser.bytesAvailable
curr_bts = ser.read(bytes_left)
rawfile.write(curr_bts)
print "Got remaining bytes..."
print curr_bts

rawfile.close()
print "closed file"

#ser.write('F')
flushBuffer()
print "CLOSED SERIAL PORT"

ser.close()





# def main():
#     try:
#         L = []
#         thread.start_new_thread(input_thread, (L,))

#         # --------------------------------------------------------------
#         # MW STUFF:
#         # ---------------------------------------------------------------
#         # if len(sys.argv) > 1:
#         #     # Client-side conduit: resource name is a script argument
#         #     resource_name = sys.argv[1]
#         # else:
#         #     # Server-side conduit: resource name is set in the experiment
#         resource_name = 'server_conduit'
#         global conduit
#         global queued
#         global reading
#         global stopflag
#         global ser
#         conduit = IPCClientConduit(resource_name)
#         conduit.initialize()
#         #reading = 0
#         #queued = 0
#         reading = 0
#         queued = 0
#         stopflag = []

#         nt = 0

#         # --------------------------------------------------------------
#         # ARDUINO STUFF:
#         # ---------------------------------------------------------------
#         #port = "/dev/ttyACM0"
#         port = "/dev/cu.usbmodem1421"
#         baudrate = 115200

#         print "# Please specify a port and a baudrate"
#         print "# using hard coded defaults " + port + " " + str(baudrate)
#         ser = Serial(port, baudrate, timeout=0.5)
#         time.sleep(1)

#         print "STARTING..."
#         #ser.is_open()
#         ser.write('S')#TRIGGER
#         flushBuffer()
#         sys.stdout.flush()

#         conduit.register_callback_for_name('pyresponse', send_pyresponse)
#         conduit.register_callback_for_name('displaying', check_mw_display)
#         #time.sleep(.005)
#         conduit.register_callback_for_name('stop_it', handle_state_mode)
#         #try:
#         #while doing_stuff==1:
#         print "Queued: ", queued
#         print "Displaying: ", reading

#         rawfile = open(os.path.join('/Users/julianarhee/Documents/MWorks/PyData', 'raw%02d.txt' % nt), 'w')

#         while not (1 in stopflag):

#             #cycle_done = 0
            

#             #print queued
#             #if queued==1:
#                 #rawfile = open(os.path.join('/Users/julianarhee/Documents/MWorks/PyData', 'raw%02d.txt' % nt), 'w')

#                 #while reading==1:
#                 #print "READING..."

#                 # while reading==0:
#                 #     pass

#                 #if reading==1:

#             curr_bts = ser.read()
#             rawfile.write(curr_bts)

#                     #nt += 1
#                     #conduit.register_callback_for_name('displaying', check_mw_display)
#                     #signal.pause() 
#                     #if reading==0:

#                 #nt += 1
#                 # rawfile.close()
#                 # print "closed file"
#                 # print nt
#                 # cycle_done=1

#                 # rawfile.close()
#                 # print "closed file"
#                 # print nt




#                 #         #time.sleep(0.005)
#                 #     else:
#                 #     #nt = 0
#                 #         strt = time.time()

#                 #         cycle_done=0
#                 #         print "GIT HERE", type(reading)
#                 #     # while reading==0:
#                 #     #     conduit.register_callback_for_name('displaying', check_mw_display)
                        
#                 #     #     print "Reading: ", reading
#                 #     #while cycle_done==0:
#                 #     while reading==1:
#                 #         #if reading==1:
#                 #             #ser.write('S')#TRIGGER
#                 #         print "READING..."

#                 #         #while getout==0:

#                 #         curr_bts = 'hi' #ser.read()
#                 #         rawfile.write(curr_bts)

#                 #         #nt += 1
#                 #         conduit.register_callback_for_name('displaying', check_mw_display)
#                 #         #signal.pause() 
#                 #         if reading==0:
#                 #             nt += 1
#                 #             cycle_done=1

#                 #     rawfile.close()
#                 #     print "closed file"
#                 #     print nt

#                 # #conduit.register_callback_for_name('pyresponse', send_pyresponse)

#             if L: 
#                 break

#                 #flushBuffer()

#         rawfile.close()
#         print "closed file"
#         print nt
#         cycle_done=1
#         ser.write('F')



#     except KeyboardInterrupt:
#         pass
#     finally:
#         conduit.finalize()



#     #ser.write('F')
#     flushBuffer()
#     print "CLOSED SERIAL PORT"

#     ser.close()


# if __name__ == '__main__':
#     try:

#         main()

#     except KeyboardInterrupt:
#         pass
#     finally:
#         print "DONE!"
#         #conduit.finalize()


# import csv

# with open('/tmp/logfile.txt','r') as din:
#     scsv=csv.reader(din)
#     for i,row in enumerate(scsv):
#         if i:
#             for h,data in zip(header,row):
#                 d[h].append(data.strip())
#         else:
#             header=row
#             d={item:[] for item in row}

# print(d)
