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
from datetime import datetime
from serial import Serial

#***DEFINE SERIAL FUNCTIONS***
def flushBuffer():
    #Flush out serial buffer
    global ser
    tmp=0;
    while tmp is not '':
        tmp=ser.read()

def save_serial_data(first_line,serial_file):
    #READ REST OF LINE FROM SERIAL DATA STREAM
    frame_counter = first_line
    frame_trigger_state = ser.readline().strip()
    screen_counter = ser.readline().strip()
    pixel_binary = ser.readline().strip()
    pixel_clock = ser.readline().strip()
    serial_time = float(ser.readline().strip())/(10**6)#convert time to secs
    time_stamp=time.time()-start_time
    # print(frame_counter, screen_counter, pixel_binary,pixel_clock, serial_time, time_stamp)
    serial_file.write('%s\t %s\t %s\t %s\t %s\t %10.6f\t %10.6f\n'%\
    (frame_counter, frame_trigger_state, screen_counter, pixel_binary, pixel_clock, serial_time, time_stamp))


#***DEFINE MWORKS FUNCTIONS***
# MW for server side conduit:
sys.path.append('/Library/Application Support/MWorks/Scripting/Python')
from mworks.conduit import IPCClientConduit


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


    if event.value == "start":
        print "Mworks started"
        #setting Mworks variable pyresponse = 'reading'
        #this is how Mworks 'knows' we are ready, and Mworks tasks continues
        conduit.send_data(conduit.reverse_codec['pyresponse'], "reading")
        queued = 1
    elif event.value == "notrunning":
        print "Mworks not running"
        queued = 0

    sys.stdout.flush()


def check_mw_display(event):
    global displaying

    if event.data == 1:
        displaying = 1

    elif event.data == 0:
        displaying = 0

    sys.stdout.flush()


def handle_state_mode(event):
    global stopflag
    stopflag.append(event.value)
    return stopflag

#***SETUP SERIAL CONNECTION***
port = "/dev/cu.usbmodem1441"#this changes if arduino connected to different USB port
baudrate = 115200

print "# Please specify a port and a baudrate"
print "# using hard coded defaults " + port + " " + str(baudrate)
ser = Serial(port, baudrate, timeout=0.5)
time.sleep(1)

flushBuffer()
sys.stdout.flush()

print "Connected  to serial port..."


# --------------------------------------------------------------
# MW STUFF: WAIT FOR SIGNAL THAT EXPERIMENT DISPLAY IS RUNNING
# ---------------------------------------------------------------
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
conduit.register_callback_for_name('stop_it', handle_state_mode)

"Connected to MW..."
print "Queued: ", queued
print "Displaying: ", reading


#***SETUP FILE FOR FILE WRITING***
parser = optparse.OptionParser()
parser.add_option('--folder-ID', action="store", dest="folder_ID", default="test", help="folder ID for data [default: test]")

(options, args) = parser.parse_args()
folder_ID = options.folder_ID

#output_path = '/Users/julianarhee/Documents/MWorks/PyData'
output_path = './out'

# Make the output paths if it doesn't already exist
try:
    os.mkdir(output_path)
except OSError, e:
    if e.errno != errno.EEXIST:
        raise e
    pass

dateFormat = '%Y%m%d%H%M%S%f'
file_time_stamp=datetime.now().strftime(dateFormat)
output_folder='%s/%s_%s/'%(output_path,folder_ID,file_time_stamp)

try:
    os.mkdir(output_folder)
except OSError, e:
    if e.errno != errno.EEXIST:
        raise e
    pass

print "Writing data to %s"%(output_folder)

 #open time file and set up headers
serial_file = open (output_folder+'serial_data.txt','w')
serial_file.write('frame_count\t frame_pin_state\t screen_count\t pixel_clock_binary\t pixel_clock_decimal\t arduino_time\t computer_time\n')


#***WAIT FOR MWORKS***
sys.stdout.flush()
old_time = 0
timer_start = time.time()
while queued == 0:
    new_time = (time.time()-timer_start)
    if new_time - old_time > 5:
        print "Waiting for Time elapsed: %5.3f s" % new_time
        sys.stdout.flush()
        old_time = new_time

print "GOT CALL FROM MW"
print "Queued : ", queued #[Python variable]

#**** Read and save Data ***
ser.write('S')#start trigger
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

print('Reading and saving serial data...')

while not (1 in stopflag):
    first_line = ser.readline().strip()
    if first_line is not '':
        save_serial_data(first_line,serial_file)

total_time = time.time()- start_time
ser.write('F')#end trigger

print('Stopped reading data...')
print "Total Time: %10.4f"%(total_time)

print('Saving data in serial buffer...')
while 1:
    first_line = ser.readline().strip()
    if first_line is not '':#
        print('Saving...')
        save_serial_data(first_line,serial_file)
    else:
        break

serial_file.close()

print('Closing serial connection...')
ser.close()
