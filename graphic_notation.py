#!/usr/bin/env python3

import time, json, os
from housepy import config, log
from housepy import drawing
from housepy.video import VideoPlayer
from braid import *

"""
ok, so it's a bummer that pyglet playback doesnt work well on python 3.
but seems like installing rtmidi on python normal might actually let braid work in 2.7. kinda badass.

"""

score = []

for filename in os.listdir("cues"):
    if filename[-5:] == ".json":
        with open(filename) as f:
            voice = json.loads(f.read())
            stub = "_".join(filename.split('.')[0].split("_")[2:])
            score.append((stub, voice))

# print(json.dumps(score, indent=4))

DURATION = 83.0

# ctx = drawing.Context(width=2000, height=250, margin=20)
# for v, voice in enumerate(score):
#     stub, points = voice
#     for point in points:
#         t, k = point
#         ctx.arc(t / DURATION, v / len(score), 3 / ctx.width, thickness=2, fill=(None if k == 'e' else (0., 0., 0.)))
# ctx.output("charts/")

print(len(score))

for v, voice in enumerate(score):
    inst = Voice(v+1, chord=(C, MYX))
    stub, points = voice
    root = (v+1) * 2
    if root > 13:
        root -= 12
    print(stub, root)
    for point in points:
        t, k = point
        inst.play_at(t, root if k == 'e' else root+1)

driver.callback(DURATION, lambda: driver.stop())
driver.play(blocking=True)

# filename = "vid_raw.mov"
# video_player = VideoPlayer(filename)
# video_player.play()

"""
would prefer like pitched particles or something

"""