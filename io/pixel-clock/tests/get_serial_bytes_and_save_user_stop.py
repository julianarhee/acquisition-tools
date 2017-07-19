#!/usr/bin/env python2
import time
from psychopy import event, visual
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
import array

# cv2.namedWindow('cam_window')
# import numpy as np
# r = np.random.rand(100,100)
# cv2.imshow('cam_window', r)

winsize = [100, 100]
win = visual.Window(fullscr=False, size=winsize, units='pix', color = (-.5,-.5,-.5))

# compute a hash from the current time so that we don't accidentally overwrite old data
run_hash = hashlib.md5(str(time.time())).hexdigest()

def flushBuffer():
    #Flush out serial buffer
    global ser
    tmp=0;
    while tmp is not '':
        tmp=ser.read()

def save_serial_data(first_byte,serial_file):

    #READ REST OF BYTES FROM SERIAL DATA STREAM
    acq_trigger = ord(first_byte)
    frame_trigger = ord(ser.read(1))
    pixel_clock = ord(ser.read(1))

     #read 4 bytes
    a=ser.read(1)
    b=ser.read(1)
    c=ser.read(1)
    d=ser.read(1)
    #assemble bytes into 32-bit integer
    byte_data=a+b+c+d
    byte_array=array.array('B',byte_data)

    timer_bytes = byte_array[0] #1st byte
    timer_bytes = (timer_bytes<<8) | byte_array[1] # 2nd byte: shift to the left 8 bits, or operation
    timer_bytes = (timer_bytes<<8) | byte_array[2] # 3rd byte: shift to the left 8 bits, or operation
    timer_bytes = (timer_bytes<<8) | byte_array[3] # 4th byte: shift to the left 8 bits, or operation
 #   float(ser.readline().strip())/(10**6)

    time_stamp=time.time()-start_time
  #  print(acq_trigger,frame_trigger,pixel_clock,timer_bytes,time_stamp)
    serial_file.write('%i\t %i\t %i\t %10.6f\t %10.6f\n'%\
    (acq_trigger, frame_trigger, pixel_clock, float(timer_bytes)/(10**6), time_stamp))


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
serial_file.write('acquisition_trigger\t frame_trigger\t pixel_clock\t arduino_time\t computer_time\n')


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

ser.write('S')#start arduino trigger
print('Triggered arduino....')


#setup to get first frame trigger
global start_time

print('Waiting for first acquisition trigger from NIDAQ...')
while 1:
    first_byte = ser.read(1)
    if first_byte is not '':#when we can read from serial, frame acquisition has started
        start_time=time.time()
        #save first set of data
        save_serial_data(first_byte,serial_file)
        break

print('Trigger received')


print('Reading data...')
print('Press ESC or q keys to stop ...')
break_flag = 0
while not break_flag:#read data until user stops
    first_byte = ser.read(1)
    if first_byte is not '':
        save_serial_data(first_byte,serial_file)
    # Break out of the while loop if these keys are registered
    if event.getKeys(keyList=['escape', 'q']):
    	break_flag = 1
    	total_time = time.time()-start_time

print('Stop key detected')

ser.write('F')#end trigger
print('Stopped reading data...')


print('Saving data in serial buffer...')
while 1:
    first_byte = ser.read(1)
    if first_byte is not '':#
        print('Saving...')
        save_serial_data(first_byte,serial_file)
    else:
        break

serial_file.close()


print('Closing serial connection...')
ser.close()

print 'Total time: %10.4f'%total_time
