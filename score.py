#!/usr/bin/env python
## python3 video playback stalls for some reason

import time, pyglet, json, sys
from housepy import config, log, util
from housepy.video import VideoPlayer

"""

Really needs to be all about weight transfer, not stepping. Which means you shouldnt have repeats.

OK, so there are continuous changes, there are events with duration, and there are zero-value percussion events. we'll start there.

"""

class Cue(object):

    d = 0

    def __init__(self, t, x, y, cue_id=None):
        if cue_id is None:
            self.id = Cue.d + 1
            Cue.d += 1
        else:
            self.id = cue_id
            if Cue.d <= cue_id:
                Cue.d = cue_id + 1
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

    def to_dict(self):
        return {'id': self.id, 't': self.t, 'x': self.x, 'y': self.y}


if sys.argv < 2:
    print("[videofile] [[cuefile]]")
    exit()
videofile = sys.argv[1]
cuefile = sys.argv[2] if len(sys.argv) > 2 else None

try:
    video_player = VideoPlayer(videofile)
except pyglet.media.avbin.AVbinException as e:
    log.error("Could not load video: %s" % log.exc(e))
    exit()

width, height = video_player.get_video_size()
cues = []

if cuefile is not None:
    try:
        with open(cuefile) as f:
            data = json.loads(f.read())
            for cue in data:
                cues.append(Cue(cue['t'], cue['x'], cue['y'], cue['id']))
    except Exception as e:
        log.info("Could not read cuefile: %s" % cuefile)
        exit()


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


def on_draw(data):
    t = data
    for cue in cues:
        cue.draw(t)
video_player.add_callback('draw', on_draw)

video_player.play()

if len(cues):
    cues.sort(key=lambda cue: cue.t)
    with open("cues/%s_cues.json" % int(time.time()), 'w') as f:
        f.write(json.dumps([cue.to_dict() for cue in cues], indent=4))
