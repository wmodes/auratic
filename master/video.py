#!/usr/bin/python
"""video.py: play and manage threaded video as needed
Author: Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)
Copyright: 2017, MIT """

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from random import choice
import threading
import os
from subprocess import call
import json

# local modules
import videothread
from common import *

#
# Constants
#
MEDIA_BASE = 'media'
FILMDB_FILE = 'films.json'

#
# Globals
#

# A list of film records 
# (each record of which is a film dict)
film_db = []
# A dictionary of lists of films, indexed by type 
# (each record of which is a film dict)
film_lists = {}
# A dictionary of content types, indexed by trigger
# (each record of which is a film dict)
content_film_dict = {}

#
# Preparatory
#

def create_film_lists():
    """Iterate through imported database and sort list by type"""
    for film in film_db:
        if 'disabled' not in film or not film['disabled']:
            # make lists of film types
            # Note, that this means a film can be in several lists
            if 'type' in film:
                for tag in film['type']:
                    if tag not in film_lists: 
                        film_lists[tag] = [film]
                    else:
                        film_lists[tag].append(film)


def read_film_file(filename):
    """Get JSON film file. File """
    with open(filename, 'r') as fp:
        return json.load(fp)


def create_content_dict():
    """Iterate through content db and create dict keyed by trigger"""
    # look through all films in the content list
    for film in film_lists['content']:
        # if a film has a trigger key
        if 'trigger' in film:
            # get the film's trigger value
            trigger_value = film['trigger']
            # if we have not already created an entry for this trigger_value
            if trigger_value not in content_film_dict:
                # create a new list entry in the content dictionary with key trigger
                content_film_dict[trigger_value] = [film]
            else:
                # otherwise, append film to the existing list
                content_film_dict[trigger_value].append(film)

#
# Control
#


def main():
    global film_db
    film_db = read_film_file(MEDIA_BASE + '/' + FILMDB_FILE)
    create_film_lists()
    create_content_dict()
    try:
        loop_film = choice(loop_film_list)
        loop_thread = videothread.VideoThread([loop_film], debug=1)

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
            content_thread = videothread.VideoThread(MEDIA_BASE,
                    [trans1_film, content_film, trans2_film], debug=1)

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
