#!/usr/bin/env python2
import time
# from psychopy import visual, event, core, monitors, logging, tools
import numpy as np
import multiprocessing as mp
import threading
from Queue import Queue
import sys
import errno
import os
import optparse
import hashlib
from serial import Serial

def flushBuffer():
    #Flush out serial buffer
    global ser
    tmp=0;
    while tmp is not '':
        tmp=ser.read()

#set up serial connection

port = "/dev/ttyACM0"
baudrate = 115200

print "# Please specify a port and a baudrate"
print "# using hard coded defaults " + port + " " + str(baudrate)
ser = Serial(port, baudrate, timeout=0.5)
time.sleep(1)

flushBuffer()
sys.stdout.flush()

print "Connected serial port..."

print('Waiting for trigger from NIDAC...')
while 1:
    ser.write('Q')#query trigger status
    trigger_status= ord(ser.read())#read byte and convert to ASCII character
#    print(trigger_status)
    if trigger_status > 127: #any value greater than 127 indicates that pin7 is HIGH #131 corresponds to pin7 with HIGH digital read (i.e.,register status 10000011 -pins 0 and 1 are for serial comm)
        start_time=time.time()
        break
print('Trigger received')

ser.write('S')#start trigger

for x in range(0,3):
	frame_counter = ser.readline()
	pixel_clock = ser.readline()
	print('frame_counter = '+str(frame_counter))
	print('pixel_clock = '+str(pixel_clock))

ser.write('F')#end trigger