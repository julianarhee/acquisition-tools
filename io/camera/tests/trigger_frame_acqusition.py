#!/usr/bin/env python2
from pvapi import PvAPI, Camera
import time
# from psychopy import visual, event, core, monitors, logging, tools
from scipy.misc import imsave
import numpy as np
import multiprocessing as mp
import threading
from Queue import Queue
import sys
import errno
import os
import optparse


parser = optparse.OptionParser()
parser.add_option('--output-path', action="store", dest="output_path", default="/tmp/frames", help="out path directory [default: /tmp/frames]")
parser.add_option('--output-format', action="store", dest="output_format", type="choice", choices=['png', 'npz'], default='png', help="out file format, png or npz [default: png]")
parser.add_option('--use-pvapi', action="store_true", dest="use_pvapi", default=True, help="use the pvapi")
parser.add_option('--use-opencv', action="store_false", dest="use_pvapi", help="use some other camera")
parser.add_option('--write-process', action="store_true", dest="save_in_separate_process", default=True, help="spawn process for disk-writer [default: True]")
parser.add_option('--write-thread', action="store_false", dest="save_in_separate_process", help="spawn threads for disk-writer")
parser.add_option('--frame-rate', action="store", dest="frame_rate", help="requested frame rate", type="float", default=60.0)
(options, args) = parser.parse_args()

acquire_images = True
save_images = True

output_path = options.output_path
output_format = options.output_format
save_in_separate_process = options.save_in_separate_process
frame_rate = options.frame_rate

use_pvapi = options.use_pvapi

save_as_png = False
save_as_npz = False
if output_format == 'png':
    save_as_png = True
elif output_format == 'npz':
    save_as_npz = True

# Make the output paths if it doesn't already exist
try:
    os.mkdir(output_path)
except OSError, e:
    if e.errno != errno.EEXIST:
        raise e
    pass

frame_output_path=output_path+'/frames/'

try:
    os.mkdir(frame_output_path)
except OSError, e:
    if e.errno != errno.EEXIST:
        raise e
    pass

time_output_path=output_path+'/times/'

try:
    os.mkdir(time_output_path)
except OSError, e:
    if e.errno != errno.EEXIST:
        raise e
    pass





# -------------------------------------------------------------
# Camera Setup
# -------------------------------------------------------------

camera = None

if acquire_images:

    print('Searching for camera...')


    # try PvAPI

    camera = None
    cameras = []
    cam_info = None

    if use_pvapi:

        pvapi_retries = 50

        # get the camera list
        
        print('Getting camera driver..')
        
        n = 0
        camera_driver = None
        while camera_driver is None and n < pvapi_retries:
            try:
                camera_driver = PvAPI(libpath='./')
            except Exception as e:
                print('.')
                time.sleep(0.1)
                camera_driver = None
                n += 1

        print('Connecting to camera...')

        n = 0
        cam_info = None

        # Let it have a few tries in case the camera is waking up

        while cam_info is None and n < pvapi_retries:
            try:
                cameras = camera_driver.camera_list()
                cam_info = cameras[0]
                n += 1
                print '\rsearching...'
                time.sleep(0.5)

                if cameras[0].UniqueId == 0L:
                    raise Exception('No cameras found')
                time.sleep(0.5)
                camera = Camera(camera_driver, cameras[0])

                print("Bound to PvAPI camera (name: %s, uid: %s)" % (camera.name, camera.uid))

                camera.request_frame_rate(frame_rate)

            except Exception as e:

                # print("%s" % e)
                cam_info = None


    if camera is None:
        try:
            import opencv_fallback

            camera = opencv_fallback.Camera(0)

            print("Bound to OpenCV fallback camera.")
        except Exception as e2:
            print("Could not load OpenCV fallback camera")
            print e2
            exit()


# -------------------------------------------------------------
# Set up a thread to write stuff to disk
# -------------------------------------------------------------

if save_in_separate_process:
    im_queue = mp.Queue()
else:
    im_queue = Queue()

disk_writer_alive = True

def save_images_to_disk():
    print('Disk-saving thread active...')

    #open time file and set up headers
    time_output_file = open (time_output_path+'frame_times.txt','w')
    time_output_file.write('frame_number\t time_stamp\n')

    currdict = im_queue.get()
    while currdict is not None:
        time_output_file.write('%i\t %s\n' % currdict['frame_count'], currdict['time_stamp'])

         # print name
        if save_as_png:
            imsave('%s/%s.png' % (frame_output_path, currdict['frame_count']), fdict['im_array'])
        else:
            np.savez_compressed('%s/%s.npz' % (frameoutput_path, currdict['frame_count']), fdict['im_array'])

        currdict = im_queue.get()
        
    disk_writer_alive = False

    print('Disk-saving thread inactive...')
    time_output_file.close()



if save_in_separate_process:
    disk_writer = mp.Process(target=save_images_to_disk)
else:
    disk_writer = threading.Thread(target=save_images_to_disk)

# disk_writer.daemon = True

if save_images:
    disk_writer.daemon = True
    disk_writer.start()



nframes = 0
frame_accumulator = 0
t = 0
last_t = None

report_period = 60 # frames

if acquire_images:
    # Start acquiring
    camera.capture_start()
    camera.queue_frame()
    camera.capture_wait()
    camera.queue_frame()

global_clock = core.Clock()

print('Beginning imaging [Hit ESC to quit]...')

#TRIGGER STUFF HERE


start_time=global_clock.getTime()

while (global_clock.getTime()-start_time) < 30:


    if acquire_images:

        im_array = camera.capture_wait()
        camera.queue_frame()
        time_stamp=global_clock.getTime()-start_time

        nframes += 1

        if save_images:
            fdict = dict()
            fdict['im_array'] = im_array
            fdict['frame_count'] = nframes
            fdict['time_stamp'] = time_stamp
  

    if nframes % report_period == 0:
        if last_t is not None:
            print('avg frame rate: %f [Hit ESC to quit]' % (report_period / (time_stamp - last_t)))
        last_t = time_stamp

    # Break out of the while loop if these keys are registered
    if event.getKeys(keyList=['escape', 'q']):
        break

    # if nframes > 50:
    #     break


if acquire_images:
    camera.capture_end()
    camera.close()

if im_queue is not None:
    im_queue.put(None)

if save_images:
    hang_time = time.time()
    nag_time = 0.05

    sys.stdout.write('Waiting for disk writer to catch up (this may take a while)...')
    sys.stdout.flush()
    waits = 0
    while not im_queue.empty():
        now = time.time()
        if (now - hang_time) > nag_time:
            sys.stdout.write('.')
            sys.stdout.flush()
            hang_time = now
            waits += 1

    print waits
    print("\n")

    if not im_queue.empty():
        print("WARNING: not all images have been saved to disk!")

    disk_writer_alive = False

    if save_in_separate_process and disk_writer is not None:
        print("Terminating disk writer...")
        disk_writer.join()
        # disk_writer.terminate()
    
    # disk_writer.join()
    print('Disk writer terminated')        

