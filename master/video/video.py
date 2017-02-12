#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from random import choice
import threading
import os
from subprocess import call
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
# create a dictionary of lists
content_film_dict = {}

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


def create_content_dict():
    for film in content_film_list:
        if 'trigger' in film:
            trigger = film['trigger']
            if trigger not in content_film_dict:
                content_film_dict[trigger] = [film]
            else:
                content_film_dict[trigger].append(film)

def main():
    create_film_lists()
    create_content_dict()
    try:
        loop_film = choice(loop_film_list)
        loop = videothread.VideoThread([loop_film], debug=1)

        while True:
            max_content = len(content_film_list)-1
            print ""
            next_film = raw_input("Next video (0-%i or 'q' to quit): " % max_content)
            if ('q' in next_film):
                break
            if (str.isdigit(next_film) and int(next_film) >= 0 and int(next_film) <= max_content):
                content_film = content_film_list[int(next_film)]
            elif (next_film in content_film_dict):
                content_film = choice(content_film_dict[next_film])
            else:
                continue
            trans1_film = choice(transition_film_list)
            trans2_film = choice(transition_film_list)
            loop = videothread.VideoThread([trans1_film, content_film, trans2_film], debug=1)

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
