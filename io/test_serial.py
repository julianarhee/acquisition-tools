#!/usr/bin/python
# -*- coding: utf-8 -*-

from psychopy import event
from serial import Serial
import sys
import time
import os
from datetime import datetime

def flushBuffer():
    #Flush out Teensy's serial buffer
    tmp=0;
    while tmp is not '':
        tmp=ser.read()


port = "/dev/ttyACM0"

baudrate = 115200

if len(sys.argv) == 3:
    ser = Serial(sys.argv[1], sys.argv[2])
else:
    print "# Please specify a port and a baudrate"
    print "# using hard coded defaults " + port + " " + str(baudrate)
    ser = Serial(port, baudrate, timeout=0.5)
    time.sleep(1)
# enforce a reset before we really start
#ser.setDTR(1)
#time.sleep(0.25)
#ser.setDTR(0)

print "STARTING..."
# ser.is_open()
flushBuffer()
sys.stdout.flush()

ser.write('S')#TRIGGER
prev_ts = 0

rawfile = open(os.path.join('/tmp', 'raw.txt'), 'w')


openfile = open(os.path.join('/tmp', 'logfile.txt'), 'w')
# openfile.write('read_ts\tsent_ts\n')
openfile.write('ntrigger,pin,received\n')
# FORMAT = '%Y%m%d%H%M%S%f'

N = 0
time.sleep(0.005)
getout=0
prev_ts = 0

nt = 0
prev_nt = 0

ncycles = 100
nbytes = 8

strt = time.time()
while getout==0:
    # sys.stdout.write(ser.readline())
    # sys.stdout.flush()
    #trigg = int(ser.readline())

    # curr_ts = ser.read()
    # sys.stdout.write(str(curr_ts))

    #start_bt = ser.read(1)
    #curr_bts = ser.read(1)



    #curr_bts = ser.read(nbytes)
    # bytesToRead = ser.inWaiting()
    # #if len(curr_bts) > 0:
    # if bytesToRead == nbytes:
    curr_bts = ser.read()
    rawfile.write(curr_bts)

    #     pin = curr_bts[1]
    #     tstamp = curr_bts[2:-1]
    #     val = sum(ord(c) << (i * 8) for i, c in enumerate(tstamp[::-1]))
    #     openfile.write('%02d,%s,%s\n' % (float(nt), pin, val))
    #         #curr_ts = []
    #         #prev_nt = nt
    # else:
    #     openfile.write('%02d,%s,%s\n' % (float(nt), '0', 'NaN'))

    
    # rawfile.write(curr_bts)


    nt += 1
    #print nt

    #f = codecs.open('/tmp/raw.txt', "r")

    # bytesToRead = ser.inWaiting()
    # curr_bts = ser.read(bytesToRead)
    # print bytesToRead
    # while len(curr_bts) < nbytes:
    #     curr_bts += ser.read(bytesToRead)

    # openfile.write('%02d\t%s\n' % (float(nt), curr_bts))
    # nt += 1
    # print nt


    # if bytesToRead == nbytes:
    #     curr_bts = ser.read(bytesToRead)
    #     openfile.write('%02d\t%s\n' % (float(nt), curr_bts))
    #         #curr_ts = []
    #         #prev_nt = nt
    #     nt += 1
    #     print nt

    # curr_bts = ser.read(bytesToRead)



    #print start_bt
    # if bytesToRead==7:
    #     #curr_bt = ser.read(5)
    #     print bytesToRead
    #     curr_bt = ser.read(bytesToRead)
    #     print len(curr_bt)
    #     openfile.write('%i\t%s\n' % (nt, curr_bt))
    #     nt += 1

    if time.time() - strt >= (30*1.):
        getout=1


    # ----------
    # TO CONVERT:
    # ----------
    #tstrings = df['sent_ts']
    #tstamps = [sum(ord(c) << (i * 8) for i, c in enumerate(s[::-1])) for s in tstrings]
    
    #val = sum(ord(c) << (i * 8) for i, c in enumerate(s[::-1]))

    # # # import codecs
    # f = codecs.open('/tmp/raw.txt', 'r')
    # data = f.read()
    # tmp_packets = data.split('__')
    # bad_splits = [i for i,p in enumerate(tmp_packets) if len(p)<6]
    # if bad_splits:
    #     fix = np.where(np.diff(bad_splits)==1)[0]
    #     remove_indices = []
    #     for f in fix: # first, concatenate n and n+1 strings
    #         tmp_packets[bad_splits[f]] += tmp_packets[bad_splits[f+1]]
    #         remove_indices.append(bad_splits[f+1])
    #     tmp_packets = [i for j,i in enumerate(tmp_packets) if j not in remove_indices]

    # packets = [p for p in tmp_packets if not p=='']
    # evs = []
    # for pidx,packet in enumerate(packets):
    #     print pidx
    #     if pidx==0:
    #         packet = packet[1:]
    #     elif pidx==len(packets)-1:
    #         packet = packet[:-1]

    #     pin = packet.split('*', 1)[0]
    #     tstring = packet.split('*', 1)[1]
    #     pin_id = int(pin)
    #     tstamp = int(tstring) #sum(ord(c) << (i * 8) for i, c in enumerate(tstring[::-1]))
    #     evs.append([pin_id, tstamp])

    # bytesToRead = ser.inWaiting()
    # curr_ts = ser.read(bytesToRead)

    # openfile.write('%f\t%s\n' % (time.time(), curr_ts))
    #curr_ts = []


    # else:
    #     curr_ts.append(int(curr_bt))
    # if trigg==0:
    #     getout = 1

    # trigg = int(ser.readline()) #/float(1E6)#to have time in secs
    # # print type(trigg)
    # if trigg==1:
    #     print 'hi'
    # # curr_ts = ser.read(size=12)
    #     curr_ts = int(ser.readline())
    #     openfile.write('%f\t%i\n' % (time.time()-strt, curr_ts))
    
    # else:

    #     getout=1
    #interval = curr_ts)-prev_ts
    #prev_ts = curr_ts
    # print type(curr_ts)


    # if curr_ts!=prev_ts:
    # # read_ts = datetime.now().strftime(FORMAT)
    #     #read_ts = time.time()
    # #if not (curr_ts == prev_ts):
    #     # openfile.write('%i\t%s\t%s\n' % (N, datetime.now().strftime(FORMAT), curr_ts))
    #     # openfile.write('%f\t%s\n' % (read_ts-strt, curr_ts))
    #     openfile.write('%f\t%s\n' % (time.time(), curr_ts))

    #     #print curr_ts
    #     #N += 1
    #     #strt = read_ts

    #     prev_ts = curr_ts

    

# if curr_ts:
#     linefromserial = curr_ts.replace('\00', '')
#       datenow = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S   ")
#       dated_linefromserial = datenow + linefromserial
#       openfile.write(dated_linefromserial)

# print curr_ts
    #sys.stdout.write(str(read_ts))

openfile.close()
print "closed file"

ser.write('F')
flushBuffer()
print "CLOSED SERIAL PORT"

ser.close()


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
