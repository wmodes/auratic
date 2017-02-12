from time import sleep
from random import choice 
from subprocess import Popen
import sys, os, signal
import threading

from video_db import *

DEBUG = True

inter_video_delay = 0.75

#OMX_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--aspect-mode fill']
OMX_CMD = ['omxplayer', '--no-osd', '--no-keys', '--aspect-mode fill']
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


def create_film_lists():
    for film in films.values():
        if film['type'] == 'transition':
            transition_film_list.append(film)
        elif film['type'] == 'content':
            content_film_list.append(film)
        elif film['type'] == 'loop':
            loop_film_list.append(film)


def start_transition(film):
    global pgid_last_transition
    debug("filename:", film['name'])
    debug("type", film['type'])
    debug("start:", film['start'], "sec")
    debug("end:", film['start']+film['length'], "sec")
    debug("length:", film['length'], "sec")
    my_cmd = " ".join(TRANSITION_CMD + [film['name']])
    debug("cmd:", my_cmd)
    proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin, stdout=nullout)
    #sleep(film['length'])
    # save this process group id
    pgid = os.getpgid(proc.pid)
    debug("pgid:", pgid)
    pgid_last_transition = pgid
    debug("setting kill timer:", film['length'], "sec")
    threading.Timer(film['length'], stop_transition, [pgid]).start()

def stop_transition(pgid):
    global pgid_last_transition
    try:
        debug("Kiling", pgid)
        os.killpg(pgid, signal.SIGTERM)
        pgid_last_transition = None
    except:
        debug("Couldn't signal", pgid)
        pass


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
    my_cmd = " ".join(CONTENT_CMD + [film['name']])
    debug("cmd:", my_cmd)
    #proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin, stdout=nullout)
    proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin)
    # save this process group id
    pgid = os.getpgid(proc.pid)
    debug("pgid:", pgid)
    pgid_last_content = pgid
    if (film['length']):
        debug("setting kill timer:", film['length'], "sec")
        threading.Timer(film['length'], stop_content, [pgid]).start()


def stop_content(pgid):
    global pgid_last_content
    try:
        debug("Kiling", pgid)
        result = os.killpg(pgid, signal.SIGTERM)
        debug("Result", result)
        pgid_last_content = None
    except:
        debug("Couldn't signal", pgid)
        pass


def stop_content_in_a_sec(pgid):
    threading.Timer(inter_video_delay, stop_content, [pgid]).start()


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
            transition = choice(transition_film_list)
            start_transition(transition)
            sleep(transition['length'] - inter_video_delay)
            content = content_film_list[next_film]
            start_content(content)
            sleep(content['length'] - inter_video_delay)
            transition = choice(transition_film_list)
            start_transition(transition)
            sleep(transition['length'] - inter_video_delay)
            #start_loop(loop)
            sleep(5)

    except KeyboardInterrupt:
        print "Done."
        # close our null file handles
        nullin.close()
        nullout.close()

if __name__ == "__main__":
    main()
