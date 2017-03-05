#!/usr/bin/python
"""videothread.py: Threaded, stopable video player class
Author: Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)
Copyright: 2017, MIT """

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import threading
import subprocess
import sys
import signal
import os
import time

# local imports
import ffprobe

INTER_VIDEO_DELAY = 0.75

OMX_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--aspect-mode fill']
CONTENT_CMD = OMX_CMD + ['--layer 4', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer1']
TRANSITION_CMD = OMX_CMD + ['--layer 5', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer2']
LOOP_CMD = OMX_CMD + ['--layer 1', '--loop', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer3']

nullin = open(os.devnull, 'r')
nullout = open(os.devnull, 'w')


class VideoThread(threading.Thread):
    """Thread class with a stop() method. The thread itself checks
    regularly for the stopped() condition."""
    _example = """
        The class takes a list containing one or more dictionaries containing
        data about the videos to be played:
            [{'name': "loop-idle1",         # if omitted, uses 'file'
                'file': "loop-idle1.mp4",   # looks in 'mediabase' for media
                'type': 'loop',             # loop, transition, content, etc
                'start': 0.0,               # if omitted, assumes 0
                'length': 0.0,              # if omitted, assumes len(filename)
                'disabled': True,           # if omitted, assumes False
                'trigger': 'item'           # if type=content, specifies trigger
             },]
        """

    def __init__(self, playlist=None, media_dir=".", debug=0):
        super(VideoThread, self).__init__()
        self._stop = threading.Event()
        self.media_dir = media_dir
        self.playlist = playlist
        self._debug_flag = debug
        self._last_debug_caller = None
        self._current_video = None
        self._player_pgid = None

    def set_sequence(self, playlist=None):
        self.playlist = playlist

    def stop(self):
        self._debug("Stop flag set")
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def debug(self, debug_flag):
        self._debug_flag = debug_flag

    def _debug(self, *args, **kwargs):
        """Produce debug message, indenting if from same calling function"""
        level = 1
        if ("level" in kwargs):
            level = kwargs["level"]
        elif("l" in kwargs):
            level = kwargs["l"]
        if (self._debug_flag >= level):
            text = " ".join(list(map(str, args)))
            # get name of calling function
            caller = sys._getframe(1).f_code.co_name
            if (caller == self._last_debug_caller):
                print "  debug: %s: %s" % (caller, text)
            else:
                print "debug: %s: %s" % (caller, text)
            # save last calling function
            self._last_debug_caller = caller

    def run(self):
        if not isinstance(self.playlist, list):
            raise ValueError(self._example)
        for video in self.playlist:
            if not self.stopped():
                self._start_video(video)

    def _start_video(self, video):
        """Starts a video. Takes a video object """
        filename = self.media_dir + '/' + video['file']
        if not isinstance(video, dict):
            raise ValueError(self._example)
        if 'name' in video:
            name = video['name']
        else:
            name = video['file']
        if 'disabled' in video and video['disabled']:
            self._debug("Not played:", name, "disabled")
            return
        self._debug("Starting %s in %s" % (name, self.media_dir)
        # get length
        if ('length' in video and (video['length'] != 0.0 or video['type'] == 'loop')):
            length = video['length']
        else:
            length = self._get_length(filename)
        # get start
        if 'start' in video:
            start = video['start']
        else:
            start = 0.0
        # if start is too large, set it to 0 (unless type=loop)
        if (video['type'] != 'loop' and start >= length):
            start = 0.0
        # store this for later
        self._current_video = video
        # debugging output
        self._debug("name: %s (%s)" % (name, filename))
        self._debug("type: %s, start: %.1fs, end: %.1fs, len: %.1fs" %
                      (video['type'], start, start+length, length))
        # construct the player command
        if (video['type'] == 'loop'):
            my_cmd = " ".join(LOOP_CMD + [filename])
        elif (video['type'] == 'transition'):
            my_cmd = " ".join(TRANSITION_CMD + ['--pos', str(video['start']), filename])
        else: 
            my_cmd = " ".join(CONTENT_CMD + ['--pos', str(video['start']), filename])
        self._debug("cmd:", my_cmd, l=2)
        # launch the player, saving the process handle
        # TODO: after debugging, replace 'if True' with 'try' and enable 'except'
        if True:
        # try:
            proc = None
            if (self._debug >= 3):
                proc = subprocess.Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin)
            else:
                proc = subprocess.Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin, stdout=nullout)
            # save this process group id
            pgid = os.getpgid(proc.pid)
            self._player_pgid = pgid
            self._debug("Starting process: %i (%s)" % (pgid, video['name']))
            # wait in a tight loop, checking if we've received stop event or time is over
            start_time = time.time()
            while (not self.stopped() and
                   (time.time() <= start_time + video['length'] - INTER_VIDEO_DELAY)):
                pass
            # If type=loop and length=0, loop forever
            if (video['type'] != 'loop' and length == 0.0):
                self._debug("Looping indefinitely for %i (%s)" %
                              (pgid, name))
            # otherwise, kill it
            else:
                self._debug("setting %.2fs kill timer for %i (%s)" %
                              (INTER_VIDEO_DELAY, pgid, video['name']))
                threading.Timer(INTER_VIDEO_DELAY, 
                                self._stop_video_, [pgid, video['name']]).start()
        # except:
        #     self._debug("Unable to start video", name, l=0)

    def _stop_video(self, pgid, name):
        try:
            self._debug("Killing process %i (%s)" % (pgid, name))
            os.killpg(pgid, signal.SIGTERM)
            self._player_pgid = None
            self._current_video = None
        except OSError:
            self._debug("Couldn't terminate %i (%s)" % (pgid, name))
            pass

    def _get_length(self, filename):
        self._debug("Getting duration of %s" % filename)
        return ffprobe.duration(filename)


def main():
    films = [
        {'name': "idle_2",
            'file': "idle_2.mp4",
            'type': 'loop',
            'layer': 1,
         },
        {'name': "tv-color-bars-distorted",
            'file': "tv-color-bars-distorted.mp4",
            'type': 'transition',
            'length': 1.0,
            'layer': 9,
         },
        {'name': "tv-static-transition",
            'file': "tv-static-transition.mp4",
            'type': 'transition',
            'length': 1.0,
            'layer': 9,
         },
        {'name': "1960s-baltimore-family",
            'file': "1960s-baltimore-family.mp4",
            'type': 'content',
            'length': 10.0,
            'layer': 5,
         },
        ]
    print "Starting sequence"
    video = VideoThread([films[1], films[3], films[2]], debug=2)
    video.start()
    print "Sequence started"
    raw_input("Press enter to kill video")
    video.stop()

if __name__ == "__main__":
    main()
