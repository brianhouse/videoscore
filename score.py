#!/usr/bin/env python
## python3 video playback stalls for some reason

import time, pyglet, json, sys
from housepy import config, log, util

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


# load files
videofile = sys.argv[1] if len(sys.argv) > 1 else None
cuefile = sys.argv[2] if len(sys.argv) > 2 else None
if videofile is None:
    videofile = raw_input("Videofile: ")
if cuefile is None:
    cuefile = raw_input("Cuefile [new]: ")
if not len(cuefile):
    cuefile = None

# read in cues
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

# start video player
from housepy.video import VideoPlayer
try:
    video_player = VideoPlayer(videofile)
except pyglet.media.avbin.AVbinException as e:
    log.error("Could not load video: %s" % log.exc(e))
    exit()
width, height = video_player.get_video_size()

# video event handlers
quality = None

def on_key_press(data):
    global quality
    t, key = data
    quality = key
    log.info("Quality is %s" % quality)
video_player.add_callback('key', on_key_press)

def on_key_release(data):
    global quality
    t, key = data
    if key == quality:
        quality = None
    log.info("Quality is %s" % quality)
video_player.add_callback('key_release', on_key_release)

def on_click(data):
    t, x, y, modifiers = data
    print(modifiers)
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

# do it
video_player.play()

# save cues
if cuefile is None:
    cuefile = "cues/%s_cues.json" % int(time.time())
prompt = "Save cuefile [%s]: " % cuefile
filename = raw_input(prompt)
if len(filename):
    cuefile = filename
if len(cues):
    cues.sort(key=lambda cue: cue.t)
    with open(cuefile, 'w') as f:
        f.write(json.dumps([cue.to_dict() for cue in cues], indent=4))
    log.info("Wrote %s" % cuefile)
