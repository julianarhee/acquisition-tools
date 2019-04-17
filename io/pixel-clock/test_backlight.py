#!/usr/bin/env python2
import time
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
from datetime import datetime
import atexit

# compute a hash from the current time so that we don't accidentally overwrite old data
#run_hash = hashlib.md5(str(time.time())).hexdigest()

global first_write
first_write = 0
def flushBuffer():
    #Flush out serial buffer
    global ser
    tmp=0;
    while tmp is not '':
        tmp=ser.read()

# def exit_handler():
#     #perform actions if script stopped by Ctrl+C


def read_4bytes(ser, dtype='B'):
    # read 4 bytes
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

    return timer_bytes

def byte_to_codes(ser, dtype='B'):
    byte = ser.read(1)
    byte_array = array.array('B', byte)#
    
    # Arduino sending masked 4-bits, read as 01111000
    # Shift 3 to get pin 3, shift 4 to read pins 4-6 as 3-bit num: 
    pixel_byte, backlight_byte = (byte_array[0]>>4), (byte_array[0]>>3) & 1 

    #print ord(byte), byte_array, backlight_byte, pixel_byte

    return pixel_byte, backlight_byte
   
def save_serial_data(first_byte,serial_file):
    global first_write
    global timer_start

    #FIRST BYT CONTAINS INFO ABOUT ACQUISITION AND FRAME TRIGGER
    registerD = array.array('B',first_byte)#conver to python-readble bytes
    acq_trigger = (registerD[0]>> 6) & 0x1
    frame_trigger =  (registerD[0] >> 7) & 0x1

    #READ REST OF BYTES FROM SERIAL DATA STREAM
    pixel_clock, backlight_sensor = byte_to_codes(ser, dtype='B')
    timer_bytes = read_4bytes(ser, dtype='B')
    
    if first_write == 0:
        timer_start = timer_bytes
        first_write = 1
    relative_timer_bytes = timer_bytes-timer_start

    absolute_time_stamp = time.clock()
    relative_time_stamp = absolute_time_stamp-start_time
#   print(acq_trigger,frame_trigger,pixel_clock)
    serial_file.write('%i\t%i\t%i\t%i\t%i\t%i\t%10.6f\t%10.6f\n'%\
    (acq_trigger, frame_trigger, pixel_clock, backlight_sensor, timer_bytes, relative_timer_bytes, absolute_time_stamp, relative_time_stamp))



parser = optparse.OptionParser()
parser.add_option('--output-path', action="store", dest="output_path", default="/Users/julianarhee/Documents/MWorks/PyData/", help="out path directory [default: /tmp/serial]")
parser.add_option('--basename', action="store", dest="basename", default="test", help="basename of output file [default: test")

(options, args) = parser.parse_args()
output_path = options.output_path
basename = options.basename

# Make the output paths if it doesn't already exist
try:
    os.mkdir(output_path)
except OSError, e:
    if e.errno != errno.EEXIST:
        raise e
    pass

#output_folder='%s/run_%s/'%(output_path,run_hash)


output_folder = output_path+'/'
try:
    os.mkdir(output_folder)
except OSError, e:
    if e.errno != errno.EEXIST:
        raise e
    pass
 #open time file and set up headers

dateFormat = '%Y%m%d%H%M%S%f'
tStamp=datetime.now().strftime(dateFormat)
serial_file_name = '%s%s_serial_data_%s.txt' %(output_folder, basename,tStamp)

serial_file = open (serial_file_name,'w+')
serial_file.write('acquisition_trigger\tframe_trigger\tpixel_clock\tbacklight_sensor\tabosolute_arduino_time\trelative_arduino_time\t\absolute_computer_time\trelative_computer_time\n')

#set up serial connection
port = "/dev/cu.usbmodem1421"
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
        start_time=time.clock()
        #save first set of data
        save_serial_data(first_byte,serial_file)
        break

print('Trigger received')


print('Reading data...')
stopflag = []
while not (1 in stopflag):
    first_byte = ser.read(1)
    if first_byte is not '':
        save_serial_data(first_byte,serial_file)

total_time = time.time()-start_time
print('STOPPING!')

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
