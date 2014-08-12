#!/usr/bin/env python
## python3 video playback stalls for some reason

import time, pyglet, json
from housepy import config, log, util
from housepy.video import VideoPlayer

"""

Really needs to be all about weight transfer, not stepping. Which means you shouldnt have repeats.

OK, so there are continuous changes, there are events with duration, and there are zero-value percussion events. we'll start there.

"""

filename = "vid_raw.mov"
# filename = "vid2.mov"
video_player = VideoPlayer(filename)
width, height = video_player.get_video_size()

class Cue(object):

    d = 0

    def __init__(self, t, x, y):
        self.id = Cue.d + 1
        Cue.d += 1
        self.t = t
        self.x = x
        self.y = y
        log.info("Made cue [%d]: %f (%f, %f)" % (self.id, self.t, self.x, self.y))

    def hit_test(self, x, y):
        distance = util.distance((self.x * width, self.y * height), (x * width, y * height))
        return True if distance < 3 else False

    def draw(self, t):
        FADE = 1.0
        elapsed = t - self.t
        if elapsed > FADE or elapsed < 0.0:
            return
        intensity = elapsed / FADE
        # video_player.draw_rect((self.x * width) - 2, (self.y * height) - 2, 5, 5, (1., 0., 0., intensity))    
        # doesnt look like alpha channel is working...
        intensity *= 0.5
        video_player.draw_rect((self.x * width) - 2, (self.y * height) - 2, 5, 5, (1. - intensity, intensity, intensity, intensity))            

cues = []


def on_key(data):
    t, key = data
    cues.append((t, key))
video_player.add_callback('key', on_key)

def on_click(data):
    t, x, y, modifiers = data
    x /= float(width)
    y /= float(height)
    # hold down key for a color?
    if modifiers == 64:
        for cue in cues:
            if cue.hit_test(x, y):                
                cues.remove(cue)
                log.info("Removed cue [%d]" % cue.id)                                        
    else:
        cue = Cue(t, x, y)
        cues.append(cue)
video_player.add_callback('click', on_click)

# so at each frame, need a callback. depending on the temporal distance, figure out the fade of the indicator. then draw them.

def on_draw(data):
    t = data
    for cue in cues:
        cue.draw(t)
video_player.add_callback('draw', on_draw)


video_player.play()

# if len(cues):
#     with open("%s_cues.json" % int(time.time()), 'w') as f:
#         f.write(json.dumps(cues, indent=4))
