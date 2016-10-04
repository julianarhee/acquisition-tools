
import os
import pymworks
import numpy as np
import pandas as pd
from bokeh.io import gridplot, output_file, show, vplot
from bokeh.plotting import figure, reset_output
from bokeh.models import TapTool, HoverTool
from bokeh.colors import RGB
import codecs
from bokeh.models import ColumnDataSource, Range1d, Label

class TooLongError(ValueError):
    pass

def pad(seq, target_length, padding=None):
    """Extend the sequence seq with padding (default: None) so as to make
    its length up to target_length. Return seq. If seq is already
    longer than target_length, raise TooLongError.

    >>> pad([], 5, 1)
    [1, 1, 1, 1, 1]
    >>> pad([1, 2, 3], 7)
    [1, 2, 3, None, None, None, None]
    >>> pad([1, 2, 3], 2)
    ... # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
      ...
    TooLongError: sequence too long (3) for target length 2

    """
    length = len(seq)
    if length > target_length:
        raise TooLongError("sequence too long ({}) for target length {}"
                           .format(length, target_length))
    seq.extend([padding] * (target_length - length))
    return seq


def get_arduino_events(fn):
    f = codecs.open(fn, 'r')
    data = f.read()
    tmp_packets = data.split('__')
    bad_splits = [i for i,p in enumerate(tmp_packets) if len(p)<6]
    if bad_splits:
        fix = np.where(np.diff(bad_splits)==1)[0]
        remove_indices = []
        for f in fix: # first, concatenate n and n+1 strings
            tmp_packets[bad_splits[f]] += tmp_packets[bad_splits[f+1]]
            remove_indices.append(bad_splits[f+1])
        tmp_packets = [i for j,i in enumerate(tmp_packets) if j not in remove_indices]

    packets = [p for p in tmp_packets if not p=='']
    evs = []
    for pidx,packet in enumerate(packets):
        print pidx
        if pidx==0:
            packet = packet[1:]
        elif pidx==len(packets)-1:
            packet = packet[:-1]

        pin = packet.split('*', 1)[0]
        tstring = packet.split('*', 1)[1]
        try:
            pin_id = int(pin)
            #pin_id = sum(ord(c) << (i * 8) for i, c in enumerate(tstring[::-1]))
            tstamp = int(tstring) #sum(ord(c) << (i * 8) for i, c in enumerate(tstring[::-1]))
            evs.append([pin_id, tstamp])
        except ValueError as e:
            print pidx
            print pin_id
            print tstring
    return evs


def get_pixel_clock_events(dfns, remove_orphans=True):
    # """
    # Parse session .mwk files.
    # Key is session name values are lists of dicts for each trial in session.
    # Looks for all response and display events that occur within session.

    # dfns : list of strings
    #     contains paths to each .mwk file to be parsed
    
    # remove_orphans : boolean
    #     for each response event, best matching display update event
    #     set this to 'True' to remove display events with unknown outcome events
    # """

    #trialdata = {}                                                              # initiate output dict
    
    for dfn in dfns:
        df = None
        df = pymworks.open(dfn)                                                 # open the datafile

        #sname = os.path.split(dfn)[1]
        #trialdata[sname] = []

        modes = df.get_events('#state_system_mode')                             # find timestamps for run-time start and end (2=run)
        # run_idxs = np.where(np.diff([i['time'] for i in modes])<20)             # 20 is kind of arbitray, but mode is updated twice for "run"
        start_ev = [i for i in modes if i['value']==2][0]
        
        # stop_ev_ev = [i for i in modes if i['time']>start_ev['time'] and (i['value']==0 or i['value']==1)]
        run_idxs = [i for i,e in enumerate(modes) if e['time']>start_ev['time']]

        bounds = []
        for r in run_idxs: #[0]:
            try:
                # stop_ev = next(i for i in modes[r:] if i['value']==0 or i['value']==1)
                stop_ev = next(i for i in modes[r:] if i['value']==0 or i['value']==1)
            except StopIteration:
                end_event_name = 'trial_end'
                print "NO STOP DETECTED IN STATE MODES. Using alternative timestamp: %s." % end_event_name
                stop_ev = df.get_events(end_event_name)[-1]
                print stop_ev
            bounds.append([modes[r]['time'], stop_ev['time']])

        bounds[:] = [x for x in bounds if x[1]-x[0]>1]
        # print "................................................................"
        print "****************************************************************"
        print "Parsing file\n%s... " % dfn
        print "Found %i start events in session." % len(bounds)
        print "****************************************************************"

        P = []
        for bidx,boundary in enumerate(bounds):

            # print "................................................................"
            print "SECTION %i" % bidx
            print "................................................................"
            #M1:#tmp_devs = df.get_events('#stimDisplayUpdate')                      # get *all* display update events
            # tmp_devs = [i for i in tmp_devs if i['time']<= boundary[1] and\
            #             i['time']>=boundary[0]]                                 # only grab events within run-time bounds (see above)

            #M1:#devs = [e for e in tmp_devs if not e.value[0]==[None]]


            # Check stimDisplayUpdate events vs announceStimulus:
            stim_evs = df.get_events('#stimDisplayUpdate')
            devs = [e for e in stim_evs if e.value and not e.value[0]==None]
            idevs = [i for i in devs for v in i.value if 'bit_code' in v.keys()]
            tmp_pdevs = [(v['bit_code'], i.time) for i in idevs for v in i.value if 'bit_code' in v.keys()]

            # Get rid of "repeat" events from state updates.
            
            #tmp_pdevs = [p for i,p in enumerate(pdevs) if i not in nons]
            pdevs = [i for i in tmp_pdevs if i[1]<= boundary[1] and i[1]>=boundary[0]]
            nons = np.where(np.diff([i[0] for i in pdevs])==0)[0]
            pdevs = [p for i,p in enumerate(pdevs) if i not in nons]

            print "Got %i pix code events." % len(pdevs)

            P.append(pdevs)

            #pix_evs = df.get_events('#pixelClockCode')
            return P


            # ann_evs = df.get_events('#announceStimulus')

            # # SEE: AG8_160705.mwk -- issue with sevs...
            # try:
            #     sevs = [i for i in ann_evs if 'png' in i.value['name']]
            # except TypeError as e:
            #     print dfn
            #     print e

            # if not len(idevs)==len(sevs):
            #     print "MISMATCH in event counts in DF: %s" % dfn
            #     print "-------------------------"
            #     print "#stimDisplayUpdate %i and #announceStimulus %i." % (len(idevs), len(sevs))

            # #M1:#devs = [e for e in stim_evs if e.value[0] is not None]
            # im_names = sorted([i['name'] for d in idevs for i in d.value if '.png' in i['name']], key=natural_keys)


# --------------------------------------------------------------------
# MW codes:
# --------------------------------------------------------------------
fn_base = 'test_5cycle_poll1ms_2'
# data_dir = '/home/juliana/Downloads'
mw_data_dir = '/Users/julianarhee/Documents/MWorks/Data'
# mw_fn = 'test_trigger.mwk'
# mw_fn = 'test_trigger_5cyc.mwk'
#mw_fn = 'test_1cycle.mwk'
# mw_fn = 'test_2cycle.mwk'
# mw_fn = 'test_10cycle.mwk'
mw_fn = fn_base+'.mwk'
dfn = os.path.join(mw_data_dir, mw_fn)
dfns = [dfn]
# df = pymworks.open(dfn)
# pix = df.get_events('#pixelClockCode')

P = get_pixel_clock_events(dfns)
pevs = [p for p in P if len(p)][0]
#pevs = P[0]

n_codes = set([i[0] for i in pevs])
if len(n_codes)<16:
    print "Check pixel clock -- missing bit values..."
mw_times = np.array([i[1] for i in pevs])
mw_codes = np.array([i[0] for i in pevs])

# mw_codes = mw_codes[1:]
# mw_times = mw_times[1:]

# --------------------------------------------------------------------
# ARDUINO codes:
# --------------------------------------------------------------------
ard_data_dir = '/Users/julianarhee/Documents/MWorks/PyData'
# ard_fn = 'raw00.txt'
ard_fn = fn_base+'.txt'
ard_dfn = os.path.join(ard_data_dir, ard_fn)

evs = get_arduino_events(ard_dfn)
ard_times = np.array([i[1] for i in evs])
ard_codes = np.array([i[0] for i in evs])


# filter out bad ones -- codes:

search_reverse = False
if search_reverse is True:
    mw_codes_source = mw_codes[::-1] # reverse serach to find last instance
    ard_codes_source = ard_codes[::-1]
    ard_times_source = ard_times[::-1]
else:
    mw_codes_source = mw_codes
    ard_codes_source = ard_codes
    ard_times_source = ard_times

match_idxs = []
found_idx = 0
curr_idx = 0
for mw_val in mw_codes_source:
    ard_bank = ard_codes_source[curr_idx:]
    found_idx = next(ard_idx for ard_idx,ard_val in enumerate(ard_bank) if ard_val==mw_val)
    curr_idx += found_idx
    match_idxs.append(curr_idx)
tmp_matched_ard_codes = ard_codes_source[match_idxs]
tmp_matched_ard_times = ard_times_source[match_idxs]
if search_reverse is True:
    matched_ard_codes = tmp_matched_ard_codes[::-1]
    matched_ard_times = tmp_matched_ard_times[::-1]
else:
    matched_ard_codes = tmp_matched_ard_codes
    matched_ard_times = tmp_matched_ard_times



t_ard = matched_ard_times - matched_ard_times[0]
# t_mw = mw_times[0:len(matched_ard_times)] - mw_times[0]
t_mw = mw_times[0:len(matched_ard_times)] - mw_times[0]
reldiffs = t_mw - t_ard
reldiffs = reldiffs #[0:-2]
hist, edges = np.histogram(reldiffs, bins=100)

# TOOLS="pan,wheel_zoom,box_zoom,reset,hover,previewsave"
# p1 = figure(title="Relative time interval diffs (mw-ard)",tools=TOOLS,
#             background_fill_color="#E8DDCB")
# p1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
#         fill_color="#036564", line_color="#033649")

# output_file('histogram.html', title="histogram.py example")

# show(gridplot(p1, ncols=2, plot_width=400, plot_height=400, toolbar_location=None))



# filter out bad ones -- times:
# this doesnt seem to work so well... tried w/ count reqs 1000

# t_ard = ard_times - ard_times[0]
# t_mw = mw_times - mw_times[0]
# matched_ts = [np.where(t_ard==min(t_ard, key=lambda x: abs(float(x) - t)))[0][0] for t in t_mw]

# matched_ard_times = ard_times[matched_ts]
# ard = ard_codes[1:]
# matched_ard_codes = ard_codes[matched_ts]



# # pad shorter vector to do change-by-change
# import copy
# if len(ard_codes) < len(mw_codes):
#     ard_codes_pad = pad(list(ard_codes), len(mw_codes), padding=-1)
#     ard_times_pad = pad(list(ard_times), len(mw_codes), padding=-1)
#     mw_codes_pad = copy.deepcopy(mw_codes)
# elif len(ard_times) > len(mw_codes):
#     mw_codes_pad = pad(list(mw_codes), len(ard_codes), padding=-1)
#     mw_times_pad = pad(list(mw_times), len(ard_codes), padding=-1)
#     ard_codes_pad = copy.deepcopy(ard_codes)


match = []
fails = []
# for idx,pair in enumerate(zip(mw_codes_pad, ard_codes_pad)):
for idx,pair in enumerate(zip(mw_codes, matched_ard_codes)):
    if pair[0]==pair[1]:
        match.append(1)
    else:
        match.append(0)
        fails.append(idx)




####### FIGURE 1 ###########

# Get unique color for each code value:

colors = []
for i in range(len(n_codes)):
    got_unique = False
    while got_unique is False:
        r = np.random.randint(255)
        g = np.random.randint(255)
        b = np.random.randint(255)
        if RGB(r,g,b) not in set(colors):
            colors.append(RGB(r,g,b)) 
            got_unique = True

matched_colors = [colors[i] for i in mw_codes]
ard_matched_colors = [colors[i] for i in matched_ard_codes]


# hover = HoverTool(
#         tooltips=[
#             ("index", "$index"),
#             ("(x,y)", "($x, $y)"),
#             ("desc", "@desc"),
#         ]
#     )



#match_idx = [idx for idx,match in enumerate(matches)]    
#TOOLS = [HoverTool(),'box_zoom','reset','box_select']

reset_output()
TOOLS="pan,wheel_zoom,box_zoom,reset,hover,previewsave"
s1 = figure(width=1000, plot_height=500, tools=TOOLS, title='MWorks Pixel Clock Codes') # ,tools = TOOLS
s1.yaxis.axis_label = 'ARD codes | MW Codes'

#x1 = p_times #range(len(p_codes)) #p_times
x1 = (np.array(mw_times) - mw_times[0]) / 1E3
y1 = mw_codes

x2 = (np.array(matched_ard_times) - matched_ard_times[0]) / 1E3
y2 = matched_ard_codes

s1.circle(x1,np.ones(len(x1))+0.2,color=matched_colors,size=10)
s1.circle(x1,match,color='red',size=5)
s1.circle(x2,np.ones(len(x2))+0.1,color=ard_matched_colors,size=10)

# s2 = figure(width=1000, plot_height=500, title=None) #,tools = TOOLS
# s2.circle(x2,np.ones(len(x2))+0.2,color=ard_matched_colors,size=10)
# #s2.circle(x1,match,color='red',size=5)
# s2.xaxis.axis_label = 'Time since 1st event (ms)'
# s2.yaxis.axis_label = 'Arduino Codes'

# p = gridplot([[s1], [s2]])
# output_file("pc_codes_match.html")
# show(p)


hist, edges = np.histogram(reldiffs/1E3, bins=100)
p1_title = "Relative time interval diffs (MW - ARD), median %.2f ms" % np.median(reldiffs/1E3)
p1 = figure(title=p1_title,tools=TOOLS,
            background_fill_color="#E8DDCB")
p1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
        fill_color="#036564", line_color="#033649")
#median_report = "Median interval: %.2f ms" % np.median(reldiffs/1E3)
#mytext = Label(x=0, y=1000, text=median_report)
#p1.add_layout(mytext)

ard_match_diffs = np.diff(match_idxs)
ard_hist, ard_edges = np.histogram(ard_match_diffs, bins=100)
p2_title = "ARD match indices, median %.2f ms" % np.median(ard_match_diffs)
p2 = figure(title=p2_title,tools=TOOLS,
            background_fill_color="#E8DDCB")
p2.quad(top=ard_hist, bottom=0, left=ard_edges[:-1], right=ard_edges[1:],
        fill_color="#036564", line_color="#033649")

fig_name = fn_base+'.html'
output_file('../tests/'+fig_name)

show(gridplot([[s1], [p1], [p2]]))

#show(gridplot(s1, p1, ncols=2, plot_width=400, plot_height=400))

#p = gridplot([[s1], [s2]])
#output_file("pc_codes_match.html")
# show(p)



# from bokeh.plotting import figure, output_file, show, ColumnDataSource
# from bokeh.models import HoverTool

# output_file("toolbar.html")

# source = ColumnDataSource(
#         data=dict(
#             x=[1, 2, 3, 4, 5],
#             y=[2, 5, 8, 2, 7],
#             desc=['A', 'b', 'C', 'd', 'E'],
#         )
#     )

# hover = HoverTool(
#         tooltips=[
#             ("index", "$index"),
#             ("(x,y)", "($x, $y)"),
#             ("desc", "@desc"),
#         ]
#     )

# p = figure(plot_width=400, plot_height=400, tools=[hover],
#            title="Mouse over the dots")

# p.circle('x', 'y', size=20, source=source)

# show(p)



