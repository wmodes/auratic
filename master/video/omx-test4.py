from time import sleep
from random import choice 
from subprocess import Popen, call
import sys, os, signal
import threading

from video_db import *

DEBUG = True

inter_video_delay = 0.75

OMX_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--aspect-mode fill']
#OMX_CMD = ['omxplayer', '--no-osd', '--no-keys', '--aspect-mode fill']
#CONTENT_CMD = OMX_CMD + ['--layer 4']
#TRANSITION_CMD = OMX_CMD + ['--layer 5']
#LOOP_CMD = OMX_CMD + ['--layer 1', '--loop']
CONTENT_CMD = OMX_CMD + ['--layer 4', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer1']
TRANSITION_CMD = OMX_CMD + ['--layer 5', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer2']
LOOP_CMD = OMX_CMD + ['--layer 1', '--loop', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer3']

transition_film_list = []
content_film_list = []
loop_film_list = []

pgid_last_loop = None
pgid_last_content = None
pgid_last_transition = None

active_threads = []
active_thread = None

nullin = open(os.devnull, 'r')
nullout = open(os.devnull, 'w')

last_caller = ""
def debug(*args):
    """Produce debug message, indenting if from same calling function"""
    global last_caller
    if (DEBUG):
        text = " ".join(list(map(str, args)))
        caller = sys._getframe(1).f_code.co_name
        if (caller == last_caller):
            print "  DEBUG: %s(): %s" % (caller, text)
        else:
            print "DEBUG: %s(): %s" % (caller, text)
        last_caller = caller


#
# Preparatory
#

def create_film_lists():
    for film in films:
        if 'disabled' not in film or not film['disabled']:
            if film['type'] == 'transition':
                transition_film_list.append(film)
            elif film['type'] == 'content':
                content_film_list.append(film)
            elif film['type'] == 'loop':
                loop_film_list.append(film)


#
# Starting & Stopping Videos
#

def start_loop(film):
    global pgid_last_loop
    debug("filename:", film['name'])
    debug("type", film['type'])
    debug("start:", film['start'], "sec")
    debug("end:", film['start']+film['length'], "sec")
    debug("length:", film['length'], "sec")
    # kill previous video before we start
    if pgid_last_loop:
        debug("previous loop still running:", pgid_last_loop, "(stopping in a sec)")
        stop_content_in_a_sec(pgid_last_loop)
    #if pgid_last_content:
        #debug("previous content still running:", pgid_last_content, "(stopping in a sec)")
        #stop_content_in_a_sec(pgid_last_content)
    # start new video (saving the process handle)
    my_cmd = " ".join(LOOP_CMD + [film['name']])
    debug("cmd:", my_cmd)
    proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin, stdout=nullout)
    # save this process group id
    pgid = os.getpgid(proc.pid)
    debug("pgid:", pgid)
    pgid_last_loop = pgid


def start_transition(film):
    global pgid_last_transition
    debug("filename:", film['name'])
    debug("type", film['type'])
    debug("start:", film['start'], "sec")
    debug("end:", film['start']+film['length'], "sec")
    debug("length:", film['length'], "sec")
    my_cmd = " ".join(TRANSITION_CMD + ['--pos', str(film['start']), film['name']])
    debug("cmd:", my_cmd)
    proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin, stdout=nullout)
    #proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin)
    #sleep(film['length'])
    # save this process group id
    pgid = os.getpgid(proc.pid)
    debug("pgid:", pgid)
    pgid_last_transition = pgid
    debug("setting kill timer for %i: %i sec" % (pgid, film['length']))
    threading.Timer(film['length'], stop_transition, [pgid]).start()


def stop_transition(my_pgid):
    global pgid_last_transition
    try:
        debug("Kiling", my_pgid)
        os.killpg(my_pgid, signal.SIGTERM)
        pgid_last_transition = None
    except:
        debug("Couldn't signal", my_pgid)
        pass


def start_content(film):
    global pgid_last_content
    debug("filename:", film['name'])
    debug("type", film['type'])
    debug("start:", film['start'], "sec")
    debug("end:", film['start']+film['length'], "sec")
    debug("length:", film['length'], "sec")
    # kill previous video before we start
    #if pgid_last_loop:
        #debug("previous loop still running:", pgid_last_loop, "(stopping in a sec)")
        #stop_content_in_a_sec(pgid_last_loop)
    if pgid_last_content:
        debug("previous content still running:", pgid_last_content, "(stopping in a sec)")
        stop_content_in_a_sec(pgid_last_content)
    # start new video (saving the process handle)
    my_cmd = " ".join(CONTENT_CMD + ['--pos', str(film['start']), film['name']])
    debug("cmd:", my_cmd)
    proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin, stdout=nullout)
    #proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin)
    # save this process group id
    pgid = os.getpgid(proc.pid)
    debug("pgid:", pgid)
    pgid_last_content = pgid
    if (film['length']):
        debug("setting kill timer for %i: %i sec" % (pgid, film['length']))
        timer = threading.Timer(film['length'], stop_content, [pgid])
        timer.start()


def stop_content(my_pgid):
    global pgid_last_content
    try:
        debug("Kiling", my_pgid)
        result = os.killpg(my_pgid, signal.SIGTERM)
        debug("Result", result)
        pgid_last_content = None
    except:
        debug("Couldn't signal", my_pgid)
        pass


def stop_content_in_a_sec(pgid):
    threading.Timer(inter_video_delay, stop_content, [pgid]).start()

#
# Sequences
#

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

def start_sequence(content):
    global active_thread
    # kill any existing threads
    while active_threads:
        active_thread.stop()
        active_thread = None
        thread = active_threads.pop()
    active_thread = StoppableThread(target = threaded_sequence, args = (content,))
    active_thread.start()
    active_threads.append(active_thread)

def threaded_sequence(content):
    # start first transition
    start_transition(choice(transition_film_list))
    # start content
    start_content(content)
    debug("Stopped? ", active_thread.stopped())
    if active_thread.stopped():
        return
    # wait the length of the clip
    sleep(content['length'] - inter_video_delay)
    debug("Stopped? ", active_thread.stopped())
    if active_thread.stopped():
        return
    # start second transition
    start_transition(choice(transition_film_list))

#
# Main Loop
#
    

def main():

    create_film_lists()
    #print transition_film_list
    #print content_film_list

    try:
        loop = choice(loop_film_list)
        start_loop(loop)

        while True:
            max_content = len(content_film_list)-1
            print ""
            next_film = raw_input("Next video (0-%i): " % max_content)
            try:
                next_film = int(next_film)
            except:
                continue
            if (next_film < 0 or next_film > max_content):
                continue
            content = content_film_list[next_film]
            start_sequence(content)
            #sleep(transition['length'] - inter_video_delay)
            #start_loop(loop)
            #sleep(5)

    except KeyboardInterrupt:
        print ""
        print "Done."
        # close our null file handles
        call(["killall", "-9", "omxplayer", "omxplayer.bin"], stdout=nullout, stderr=nullout)
        nullin.close()
        nullout.close()

if __name__ == "__main__":
    main()
