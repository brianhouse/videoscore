#!/usr/bin/env python
## python3 video playback stalls for some reason

import time, pyglet, json, sys
from housepy import config, log, util

characters = "1234567890qwertyuiopasdfghjklzxcvbnm"
colors = [  (0, 0, 1),
            (0, 1, 0),
            (0, 1, 1),
            (1, 0, 0),
            (1, 0, 1),
            (1, 1, 0)
            ]

class Cue(object):

    d = 0

    def __init__(self, t, x, y, q, cue_id=None):
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
        self.q = q
        log.info("Made cue [%d]: %f (%f, %f) %s" % (self.id, self.t, self.x, self.y, self.q))

    def hit_test(self, x, y):
        distance = util.distance((self.x * width, self.y * height), (x * width, y * height))
        return True if distance < 3 else False

    def draw(self, t):
        FADE = 1.0
        elapsed = t - self.t
        if elapsed > FADE or elapsed < 0.0:
            return        
        intensity = 1.0 - (elapsed / FADE)
        # color = 0., 1., 0., intensity
        color = list(colors[characters.index(self.q) % len(colors)])
        color.append(intensity)        
        video_player.draw_rect((self.x * width) - 2, (self.y * height) - 2, 5, 5, color)            

    def to_dict(self):
        return {'id': self.id, 't': self.t, 'x': self.x, 'y': self.y, 'q': self.q}


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
                cues.append(Cue(cue['t'], cue['x'], cue['y'], cue['q'], cue['id']))
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
quality = '1'

def on_key_press(data):
    global quality
    t, key = data
    if key in characters:
        quality = key
        log.info("Quality is %s" % quality)
video_player.add_callback('key', on_key_press)

def on_click(data):
    t, x, y, modifiers = data
    # print(modifiers)
    x /= float(width)
    y /= float(height)
    if modifiers == 64: # command (option is 132, control is 2, shift is 1, fn is 512)
        for cue in cues:
            if cue.hit_test(x, y):                
                cues.remove(cue)
                log.info("Removed cue [%d]" % cue.id)        
    elif modifiers == 132:
        for cue in cues:
            if cue.hit_test(x, y):
                log.info("Cue [%d]: %f (%f, %f) %s" % (cue.id, cue.t, cue.x, cue.y, cue.q))
    else:
        cue = Cue(t, x, y, quality)
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
