#!/usr/bin/env python
## python3 video playback stalls for some reason

import time, pyglet, json
from housepy import config, log
from housepy.video import VideoPlayer

"""

Really needs to be all about weight transfer, not stepping. Which means you shouldnt have repeats.

"""

filename = "vid_raw.mov"
# filename = "vid2.mov"
video_player = VideoPlayer(filename)

cues = []

def keytime(data):
    t, key = data
    cues.append((t, key))

video_player.add_callback('key', keytime)
video_player.play()

if len(cues):
    with open("%s_cues.json" % int(time.time()), 'w') as f:
        f.write(json.dumps(cues, indent=4))
