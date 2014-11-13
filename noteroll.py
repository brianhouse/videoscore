#!/usr/bin/env python3

import json, datetime, time, sys, os, queue, random, pyglet
from housepy import config, log, util, osc, crashdb, animation
import numpy as np

CHANNEL = None

if len(sys.argv) > 1:
    CHANNEL = int(sys.argv[1])  # 1=bass, 2=cello, 3=viola

db = crashdb.load("notes.json")
notes = db['notes']
nts = [note[0] for note in notes]
db.close()

ctx = animation.Context(1200, 600, background=(0.9, 0.9, 0.9, 1.), fullscreen=False, title="The Patient Conflict", smooth=False)

page_duration = 5.0
margin = 1.0
hitpoint = margin / (page_duration - margin)
note_index = 0
start_t = 0
t = 0
last_t = 0
started = False

names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

treble_ledgers = {'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6, 'C': 7, 'D+': 8, 'E+': 9, 'F+': 10, 'G+': 11}
bass_ledgers =   {'F': 1, 'G': 2, 'A': 3, 'B': 4, 'C': 5, 'D': 6, 'E': 7, 'F+': 8, 'G+': 9, 'A+': 10, 'B+': 11}

def get_treble_note_name(n):
    p = n - 24
    i = n % 12
    return "%s%s" % (names[i], '+' if n > 60 and n < 68 else '')        ## this is a wack way to do this

def get_bass_note_name(n):
    p = n - 24
    i = n % 12
    return "%s%s" % (names[i], '+' if n > 64 and n < 72 else '')

def get_treble_ledger(n):
    name = get_treble_note_name(n)
    return treble_ledgers[name]

def get_bass_ledger(n):
    name = get_bass_note_name(n)
    return bass_ledgers[name]

def message_handler(location, address, data):
    if address != "/sync":
        return
    global t
    global started
    global start_t
    global last_t
    global note_index
    t = data[0]
    if int(t) == 0:
        started = False
    if not started:
        log.info("STARTING")
        started = True
        start_t = time.time()
        last_t = start_t
        note_index = 0
osc.Receiver(config['players'][CHANNEL - 1]['port'] if CHANNEL is not None else 39393, message_handler)

def draw():
    global t
    global last_t
    draw_staff()    
    if not started:
        return
    start_frame = time.time()
    t += start_frame - last_t
    last_t = start_frame    
    draw_frame(t)
    ctx.line(hitpoint, 0.0, hitpoint, 1.0, thickness=2.0)#, color=(1., 1., 1., 1.))    

def draw_staff():
    h = 0.125
    for i in range(5):
        i += 2
        ctx.line(0.0, i * h, 1.0, i * h, thickness=2.0)#, color=(1., 1., 1., 1.))    

def draw_frame(t):
    global note_index
    start_index = note_index
    while nts[start_index] < (t - margin):
        start_index += 1        
    stop_t = (t - margin) + (page_duration - margin)
    stop_index = start_index + 1
    while nts[stop_index] <= stop_t:
        stop_index += 1
        if stop_index == len(nts):
            return
    print(note_index, start_index, stop_index, len(nts))                    
    current_nts = np.array(nts[start_index:stop_index])
    current_notes = np.array(notes[start_index:stop_index])
    current_nts -= (t - margin)
    current_nts /= (page_duration - margin)
    for i, t in enumerate(current_nts):
        note = current_notes[i]        
        channel = int(note[2])
        note = int(note[1])

        if CHANNEL is not None and channel != CHANNEL:
            continue

        ## hack right here for the bentels ##
        # if channel != 1:
        #     continue

        if channel == 1 or channel == 2:
            vertical = (get_treble_ledger(note) * 0.0625) + 0.0625
        else:
            vertical = (get_bass_ledger(note) * 0.0625) + 0.0625


        # intensity = 1.0 - abs(hitpoint - t)
        # intensity /= 2.0
        if t < hitpoint:
            color = (.3, .3, .3, 1.)
        else:
            if channel == 1:
                color = (.6, 0., 0., 1.)    # red
            elif channel == 2:
                color = (0., .6, 0., 1.)    # green
            elif channel == 3:
                color = (0., 0., .6, 1.)    # blue
            elif channel == 4:
                color = (.6, 0., .6, 1.)

        vertical += 0.010
        # vertical += int(str(note_info[4])[-2]) * 0.001
        width = ((0.105 * ctx.height) / ctx.width)
        height = 0.105
        ctx.rect(t, vertical, width, height, color=color, thickness=1.0)
    note_index = start_index

ctx.start(draw)
