#!/usr/bin/env python2
import time
import numpy as np
import multiprocessing as mp
import threading
from Queue import Queue
import sys
import errno
import os

#DEFINE MWORKS FUNCTIONS
# MW for server side conduit:
sys.path.append('/Library/Application Support/MWorks/Scripting/Python')
from mworks.conduit import IPCClientConduit

def flushBuffer():
    #Flush out serial buffer
    global ser
    tmp=0;
    while tmp is not '':
        tmp=ser.read()

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



# --------------------------------------------------------------
# MW STUFF: WAIT FOR SIGNAL THAT EXPERIMENT DISPLAY IS RUNNING
# ---------------------------------------------------------------
resource_name = 'server_conduit'
global conduit
global queued
global displaying
global stopflag

conduit = IPCClientConduit(resource_name)
conduit.initialize()

#*Global variables*
#python variable 'queued' modifiied by send_pyresponse fxn;
# queued = 0 when Mworks variable pyresponse = 'notrunning'
# queued = 1 when Mworks variable pyresponse = 'start'
queued = 0

#python variable 'displaying' modified by check_mw_display fxn;
# displaying = 1 when Mworks variable displaying = 1
# displaying = 0 when Mworks variable displaying = 0
displaying = 0

#python variable 'stopflag' modified by handle_state_mode fxn; 
# fxn will append 1 to list, when MWORKS variable 'stop_it' set to 1
stopflag = []

#callback fxnsß
conduit.register_callback_for_name('pyresponse', send_pyresponse)
conduit.register_callback_for_name('displaying', check_mw_display)
conduit.register_callback_for_name('stop_it', handle_state_mode)



"Connected to MW..."
print "Queued: ", queued #[Python variable]
print "Displaying: ", displaying #[Mworks variable]

print "STARTING"


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

while not (1 in stopflag):
    s=1
   # print "Running.."

print('FINISHED!')