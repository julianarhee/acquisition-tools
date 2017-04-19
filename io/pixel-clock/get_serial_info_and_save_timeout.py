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
serial_file.write('frame_count\t screen_count\t pixel_clock_state\t computer_time\n')


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
print('Reading data...')

while (time.time()-start_time)<60:
	first_line = ser.readline().strip()
	if first_line is not '':
		frame_counter = first_line
		screen_counter = ser.readline().strip()
		pixel_clock = ser.readline().strip()
		time_stamp=time.time()-start_time
		serial_file.write('%s\t %s\t %s\t %10.4f\n'%\
	    (frame_counter, screen_counter, pixel_clock, time_stamp))
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
