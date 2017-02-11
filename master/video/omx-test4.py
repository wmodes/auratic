from time import sleep
from random import choice 
from subprocess import Popen
import os

from video_db import *

DEBUG = True

OMX_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh']
OMX_LOOP_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--loop']

transition_film_list = []
content_film_list = []

pgid_last_video = None

def debug(*args):
    if (DEBUG):
        text = " ".join(list(map(str, args)))
        print text


def create_film_lists():
    for film in films.values():
        if film['type'] == 'transition':
            transition_film_list.append(film)
        elif film['type'] == 'content':
            content_film_list.append(film)


def play_default_film(film):
    pass


def play_film_object(film):
    debug("\nfilename:", film['name'])
    debug("  type", film['type'])
    debug("  start:", film['start'])
    debug("  end:", film['start']+film['length'])
    debug("  length:", film['length'])
    nullin = open(os.devnull, 'r')
    nullout = open(os.devnull, 'w')
    #proc = Popen(['omxplayer', '--no-osd', '--no-keys', '--refresh', --loop', film], stdin=nullin)
    my_cmd = " ".join(OMX_CMD + film['name'])
    proc = Popen(my_cmd, shell=True, stdin=nullin)
    pgid_last_video = os.getpgid(proc.pid)
    sleep(film['length'])
    #debug("  proc:", proc).pid
    os.killpg(pgid_last_video, signal.SIGTERM)
    nullin.close()
    nullout.close()
    return True


def main():

    create_film_lists()
    #print transition_film_list
    #print content_film_list

    try:

        while True:
            play_film_object(choice(transition_film_list))
            play_film_object(choice(content_film_list))
        print "Done."

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
