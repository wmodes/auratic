from time import sleep
from random import choice 
from subprocess import Popen
import sys, os, signal
import threading

from video_db import *

DEBUG = True

inter_video_delay = 0.5

CONTENT_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', 
        '--aspect-mode fill', '--layer 2']
TRANSITION_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', 
        '--aspect-mode fill', '--layer 5']
LOOP_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--loop', '--aspect-mode fill']

transition_film_list = []
content_film_list = []

pgid_last_content = None
pgid_last_transition = None

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


def start_default_film(film):
    pass


def start_transition(film):
    global pgid_last_transition
    debug("filename:", film['name'])
    debug("type", film['type'])
    debug("start:", film['start'], "sec")
    debug("end:", film['start']+film['length'], "sec")
    debug("length:", film['length'], "sec")
    nullin = open(os.devnull, 'r')
    nullout = open(os.devnull, 'w')
    my_cmd = " ".join(TRANSITION_CMD + [film['name']])
    proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin, stdout=nullout)
    #sleep(film['length'])
    # save this process group id
    pgid = os.getpgid(proc.pid)
    debug("pgid:", pgid)
    pgid_last_transition = pgid
    # close our null file handles
    nullin.close()
    nullout.close()
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


def start_content(film):
    global pgid_last_content
    debug("filename:", film['name'])
    debug("type", film['type'])
    debug("start:", film['start'], "sec")
    debug("end:", film['start']+film['length'], "sec")
    debug("length:", film['length'], "sec")
    nullin = open(os.devnull, 'r')
    nullout = open(os.devnull, 'w')
    # kill previous video before we start
    if pgid_last_content:
        debug("previous vid still running:", pgid_last_content, "(stopping in a sec)")
        stop_content_in_a_sec(pgid_last_content)
    # start new video (saving the process handle)
    my_cmd = " ".join(CONTENT_CMD + [film['name']])
    proc = Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin, stdout=nullout)
    # save this process group id
    pgid = os.getpgid(proc.pid)
    debug("pgid:", pgid)
    pgid_last_content = pgid
    #sleep(film['length'] - inter_video_delay)
    # close our null file handles
    nullin.close()
    nullout.close()
    debug("setting kill timer:", film['length'], "sec")
    threading.Timer(film['length'], stop_content, [pgid]).start()


def stop_content(pgid):
    global pgid_last_content
    try:
        debug("Kiling", pgid)
        os.killpg(pgid, signal.SIGTERM)
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

        while True:
            transition = choice(transition_film_list)
            start_transition(transition)
            content = choice(content_film_list)
            start_content(content)
            sleep(content['length'] - inter_video_delay)

    except KeyboardInterrupt:
        print "Done."

if __name__ == "__main__":
    main()
