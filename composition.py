#!/usr/bin/env python3

import sys, json, os, random, subprocess, time
from housepy import config, log, osc, crashdb
from braid import *

# cuefile = sys.argv[1] if len(sys.argv) > 1 else None
# if cuefile is None:
#     cuefile = os.path.abspath(input("Cuefile: "))
# log.info("Reading %s" % cuefile)
cuefile = "cues/firstreal_5.json"

# read in cues
cues = []
if cuefile is not None:
    try:
        with open(cuefile) as f:
            cues = json.loads(f.read())
    except Exception as e:
        log.info("Could not read cuefile: %s (%s)" % (cuefile, log.exc(e)))
        exit()
# print(cues)

chord = C4, DOR
chord = None
v1 = Voice(1, chord=chord)
v2 = Voice(2, chord=chord)
v3 = Voice(3, chord=chord)
# v4 = Voice(4, chord=chord)

# play_at(self, t, step, velocity=None):

# interval = 5
# interval = 3
# mapping = { '1': 1, '2': 1+interval,
#             '3': 3, '4': 3+interval,
#             '5': 5, '6': 5+interval,
#             '7': 7, '8': 7+interval,
#             '9': 9, '0': 9+interval,
#             'a': 10, 's': 10+interval,
#             'd': 11, 'f': 11+interval,
#             # 'g': 12, 'h': 12+interval,
#             # 'j': 13, 'k': 13+interval,
#             }

# mapping = { '1': F3, '2': B3,
#             '3': G3, '4': C4,
#             '5': A3, '6': D4,
#             '7': B3, '8': E4,
#             '9': C4, '0': F4,
#             'a': D4, 's': G4,
#             'd': E4, 'f': A4,
#             'g': F4, 'h': B4,
#             'z': G4, 'x': C5,
#             'c': A4, 'v': D5,
#             'b': B4, 'n': E5,
#             'q': C5, 'w': F5
#             }

pairs = [   (F3, B3),
            (G3, C4),
            (A3, D4),
            (B3, E4),
            (C4, F4),
            (D4, G4),
            (E4, A4),
            (F4, B4),
            (G4, C5),
            (A4, D5),
            (B4, E5),
            (C5, F5)
            ]
# shuffle(pairs)
pairs = [(60, 65), (59, 64), (57, 62), (62, 67), (72, 77), (65, 71), (67, 72), (55, 60), (53, 59), (64, 69), (69, 74), (71, 76)]
# print(pairs)
# exit()

soldiers = [    ('1', '2'),
                ('3', '4'),
                ('5', '6'),
                ('7', '8'),
                ('9', '0'),
                ('a', 's'),
                ('d', 'f'),
                ('g', 'h'),
                ('j', 'k'),
                ('z', 'x'),
                ('c', 'v'),
                ('b', 'n'),
                ]

mapping = {}
for s, feet in enumerate(soldiers):
    for f, foot in enumerate(feet):
        mapping[foot] = pairs[s][f]

# print(mapping)

# exit()

notes = []
for cue in cues:

    # if cue['x'] > 0.75:
    #     v = v4
    #     # continue            ##              turn voices on and off
    # elif cue['x'] > 0.5:
    #     v = v3
    #     # continue            ##
    # elif cue['x'] > 0.25:
    #     v = v2
    #     # continue            ##
    # else:
    #     v = v1
    #     # continue            ##

    if cue['x'] > 0.66:
        v = v3
        # continue            ##              turn voices on and off
    elif cue['x'] > 0.33:
        v = v2
        # continue            ##
    else:
        v = v1
        # continue            ##

    if cue['q'] not in mapping:
        continue
    t, step, velocity = cue['t'], mapping[cue['q']], ((1.0 - cue['y']) * 0.5) + 0.5
    v.play_at(t, step, velocity)
    # root, scale = v.chord.value
    # pitch = root + scale[step]
    pitch = step
    notes.append((t, pitch, v.channel.value))

db = crashdb.load("notes.json")
db['notes'] = notes
db.close()
log.info("Wrote notes.json")
# exit()

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
