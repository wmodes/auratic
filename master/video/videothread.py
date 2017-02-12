import threading
import sys
import signal
import os
import time

OMX_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--aspect-mode fill']
CONTENT_CMD = OMX_CMD + ['--layer 4', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer1']
TRANSITION_CMD = OMX_CMD + ['--layer 5', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer2']
LOOP_CMD = OMX_CMD + ['--layer 1', '--loop', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer3']

nullin = open(os.devnull, 'r')
nullout = open(os.devnull, 'w')

class VideoThread(threading.Thread):
    """Thread class with a stop() method. The thread itself checks
    regularly for the stopped() condition.
    
    Instantiating the class requires passing a dictionary containing
    one of more dictionaries containing information about the videos 
    to be played:
        [{'name': "idle_2.mp4", # filename of the file
          'type': 'loop',       # video type: loop, transition, or content
          'start': 0.0,         # start position in video (sec)
          'length': 0.0,        # duration to play (sec)
          'layer': 1,           # omxplayer layer on which to display
          'disabled': False     # If set, record is ignored
        }]
    """

    def __init__(self, play_list):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()
        self._debug = 0
        self._last_caller = None
        self._current_video = None
        self._player_pgid = None  
        __start_sequence__(play_list)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def debug(self, debug_flag):
        self._debug = debug_flag

    def __debug_(self, *args, **kwargs):
        """Produce debug message, indenting if from same calling function"""
        if ("level" in kwargs):
            level = kwargs["level"]
        elif("l" in kwargs):
            level = kwargs["l"]
        if (level >= self.debug):
            text = " ".join(list(map(str, args)))
            caller = sys._getframe(1).f_code.co_name
            if (caller == self._last_caller):
                print "  DEBUG: %s(): %s" % (caller, text)
            else:
                print "DEBUG: %s(): %s" % (caller, text)
            self._last_caller = caller

    def __start_sequence__(self, play_list):
        for video in play_list:
            if not self.stopped():
                __debug__("Starting:", video)
                __start_video__(video)

    def __start_video__(self, video):
        self._current_video = video
        __debug_("filename:", video['name'])
        __debug_("type", video['type'])
        __debug_("start:", video['start'], "sec")
        __debug_("end:", video['start']+video['length'], "sec")
        __debug_("length:", video['length'], "sec")
        # construct the player command
        my_cmd = " ".join(TRANSITION_CMD + ['--pos', str(video['start']), video['name']])
        __debug_("cmd:", my_cmd)
        # launch the player, saving the process handle
        try:
            if (_debug):
                proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin)
            else:
                proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin, stdout=nullout)
        except:
            __debug__("Unable to start video", video['name'])
        # save this process group id
        self._player_pgid = os.getpgid(proc.pid)
        __debug_("pgid:", self._player_pgid)
        __debug_("setting kill timer for %i: %i sec" % (self._player_pgid, video['length']))
        # wait in a tight loop, checking if we've received stop event or time is over
        start_time = time.time()
        while (not self.stopped() and (time.time() >= start_time + video('length'))):
            pass
        __stop_video__()

    def __stop_video__(self):
        try:
            debug("Killing process %i (%s)" % (self._player_pgid, self._current_video['name']))
            os.killpg(self._player_pgid, signal.SIGTERM)
            self._player_pgid = None
        except:
            debug("Couldn't signal", self._player_pgid)
            pass
