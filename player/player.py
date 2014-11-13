#!/usr/bin/env python3

import sys, json, os, random, subprocess, time
from housepy import config, log, osc
from braid import *

# cuefile = sys.argv[1] if len(sys.argv) > 1 else None
# if cuefile is None:
#     cuefile = os.path.abspath(input("Cuefile: "))
# log.info("Reading %s" % cuefile)
cuefile = "firstreal_4.json"

# read in cues
cues = []
if cuefile is not None:
    try:
        with open(cuefile) as f:
            cues = json.loads(f.read())
    except Exception as e:
        log.info("Could not read cuefile: %s (%s)" % (cuefile, log.exc(e)))
        exit()

print(cues)

chord = G3, DOR
v1 = Voice(1, chord=chord)
v2 = Voice(2, chord=chord)
v3 = Voice(3, chord=chord)
v4 = Voice(4, chord=chord)

# play_at(self, t, step, velocity=None):

interval = 5
interval = 3
mapping = { '1': 1, '2': 1+interval,
            '3': 3, '4': 3+interval,
            '5': 5, '6': 5+interval,
            '7': 7, '8': 7+interval,
            '9': 9, '0': 9+interval,
            'a': 10, 's': 10+interval,
            'd': 11, 'f': 11+interval,
            # 'g': 12, 'h': 12+interval,
            # 'j': 13, 'k': 13+interval,
            }

for cue in cues:
    if cue['x'] > 0.75:
        v = v4
    elif cue['x'] > 0.5:
        v = v3
    elif cue['x'] > 0.25:
        v = v2
    else:
        v = v1
    if cue['q'] not in mapping:
        continue
    v.play_at(cue['t'], mapping[cue['q']], ((1.0 - cue['y']) * 0.5) + 0.5)




# subprocess.call("open ../vid_raw.mov", shell=True)
# time.sleep(0.6)

t = None
sync_t = time.time()

def message_handler(location, address, data):
    global t, sync_t
    t = float(data[0])
    sync_t = time.time()
receiver = osc.Receiver(23232, message_handler)

def time_f():
    if t is None:
        return 0.0
    elapsed = time.time() - sync_t    
    return t + elapsed

driver.time_f = time_f
play()
