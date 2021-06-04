# acquisition-tools
Auxiliary data acquisition tools for 2p imaging experiments. Stimulus presentation, animal face tracking, and neural data acquisition are synced using digital triggers. All code developed for imaging experiments in the Cox Lab, Harvard University. 

## Overview
Acquisition relies on Arduino and Python code to sync three components:
- **pixel clock**:   A 3- or 4-bit code provides an identifier for each frame of the stimulus monitor (60 Hz refresh rate). On each refresh, the stimulus protocol updates this code, and corresponding photodiodes physically measure these updates (custom PCB with Arduino board).
- **face camera**:  A high-resolution camera captures face and forepaw movements of head-restrained rats. Frame rate is fixed (25 Hz), and data streaming is re-triggered at the start of each block of trials. Metadata (frame triggers from neural data acquisition, timestamps, etc.) are saved to a text file. 
- **neural data**:  Neural imaging data is acquired using [ScanImage](http://scanimage.vidriotechnologies.com/display/SIH/ScanImage+Home) (1), which uses [National Instruments FlexRIO](https://www.ni.com/en-us/shop/electronic-test-instrumentation/flexrio/what-is-flexrio.html). SI frame triggers are the basic unit for syncing (~45 Hz). 

## Basic Usage
Stimulus presentation code is in `io/pixel-clock`. 

Upload the following arduino sketch:  `pixel_clock_sketch_updated_pinout.ino`

To run everything:

	$ python read_serial_data_from_mw.py 

Code for face data acquisition is in `io/camera`. There is one main script for starting the acquisition stream (Linux). The data stream will wait until it receives a start trigger. Example usage:

	$ python frame_acqusition_arduino_sync.py 

- _output-path_:  Directory to save images (frames).
- _frame-rate_:  Fixed acquisition rate (Hz). Tip, test exposure and frame rate values using the camera API.
- _basename_:  Sub-directory to save all acquisition files (meta data and raw images).



## References
1. Pologruto TA, Sabatini BL, Svoboda K. ScanImage: flexible software for operating laser scanning microscopes. _Biomed Eng Online_. 2003 May 17;2:13.
2. 
