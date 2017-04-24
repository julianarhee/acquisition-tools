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


# compute a hash from the current time so that we don't accidentally overwrite old data
run_hash = hashlib.md5(str(time.time())).hexdigest()

def flushBuffer():
    #Flush out serial buffer
    global ser
    tmp=0;
    while tmp is not '':
        tmp=ser.read()

def save_serial_data(first_line,serial_file):
    #READ REST OF LINE FROM SERIAL DATA STREAM
    frame_counter = first_line
    screen_counter = ser.readline().strip()
    pixel_binary = ser.readline().strip()
    pixel_clock = ser.readline().strip()
    serial_time = float(ser.readline().strip())/(10**6)#convert time to secs
    time_stamp=time.time()-start_time
    # print(frame_counter, screen_counter, pixel_binary,pixel_clock, serial_time, time_stamp)
    serial_file.write('%s\t %s\t %s\t %s\t %10.6f\t %10.6f\n'%\
    (frame_counter, screen_counter, pixel_binary, pixel_clock, serial_time, time_stamp))


parser = optparse.OptionParser()
parser.add_option('--output-path', action="store", dest="output_path", default="/tmp/serial", help="out path directory [default: /tmp/serial]")

(options, args) = parser.parse_args()
output_path = options.output_path

# Make the output paths if it doesn't already exist
try:
    os.mkdir(output_path)
except OSError, e:
    if e.errno != errno.EEXIST:
        raise e
    pass

output_folder='%s/run_%s/'%(output_path,run_hash)

try:
    os.mkdir(output_folder)
except OSError, e:
    if e.errno != errno.EEXIST:
        raise e
    pass
 #open time file and set up headers
serial_file = open (output_folder+'serial_data.txt','w')
serial_file.write('frame_count\t screen_count\t pixel_clock_binary\t pixel_clock_decimal\t arduino_time\t computer_time\n')


#set up serial connection
port = "/dev/cu.usbmodem1441"
baudrate = 115200

print "# Please specify a port and a baudrate"
print "# using hard coded defaults " + port + " " + str(baudrate)
ser = Serial(port, baudrate, timeout=0.5)
time.sleep(1)

flushBuffer()
sys.stdout.flush()

print "Connected serial port..."

ser.write('S')#start arduino trigger
print('Triggered arduino....')


#setup to get first frame trigger
global start_time

print('Waiting for first trigger from NIDAQ...')
while 1:
    first_line = ser.readline().strip()
    if first_line is not '':#when we can read from serial, frame acquisition has started
        start_time=time.time()
        #save first set of data
        save_serial_data(first_line,serial_file)
        break

print('Trigger received')


print('Reading data...')

while (time.time()-start_time)<60:
	first_line = ser.readline().strip()
	if first_line is not '':
		save_serial_data(first_line,serial_file)
ser.write('F')#end trigger
print('Stopped reading data...')

# frame_counter = ser.readline()
# screen_counter = ser.readline()
# pixel_clock = ser.readline()
# # time_stamp=time.time()-start_time
# moreBytes = ser.inWaiting()

serial_file.close()

print('Closing serial connection...')
ser.close()
