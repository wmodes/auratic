#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from random import choice
import threading
import os
# local modules
import videothread
from video_db import *

"""video.py: play and manage threaded video as needed"""
__author__ = "Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)"
__copyright__ = "2017, MIT"


#
# Constants
#

DEBUG = True
inter_video_delay = 0.75

#
# Globals
#

transition_film_list = []
content_film_list = []
loop_film_list = []


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


def main():
    create_film_lists()
    try:
        loop_film = choice(loop_film_list)
        loop = videothread.VideoThread([loop_film])

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
            trans1_film = choice(transition_film_list)
            trans2_film = choice(transition_film_list)
            content_film = content_film_list[next_film]
            loop = videothread.VideoThread([trans1_film, content_film, trans2_film])

    except KeyboardInterrupt:
        print ""
        print "Done."
        nullin = open(os.devnull, 'r')
        nullout = open(os.devnull, 'w')
        call(["killall", "-9", "omxplayer", "omxplayer.bin"], stdout=nullout, stderr=nullout)
        nullin.close()
        nullout.close()


if __name__ == "__main__":
    main()
