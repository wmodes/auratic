#!/usr/bin/python
"""master.py: listen for RFID from active USB port and trigger chart recorder and video
Author: Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)
Copyright: 2017, MIT"""

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# local modules
from common import *
from devices import *
from video import *

#
# Constants
#


#
# Globals
#
old_video_threads = []
# A list of film records 
# (each record of which is a film dict)
film_list = []
# A dictionary of lists of films, indexed by type 
# (each record of which is a film dict)
film_dict = {}
# A dictionary of content types, indexed by trigger
# (each record of which is a film dict)
content_dict = {}


def create_object_dict(object_list):
    """Iterate through content db and create dict keyed by trigger"""
    # look through all films in the content list
    object_dict = {'default': 'default'}
    for obj in object_list:
        # if a film has a trigger key
        if 'trigger' in obj and 'rfid' in obj:
            # get the object's trigger and rfid values
            trigger_value = obj['trigger']
            rfid_value = obj['rfid']
            # create an entry of triggers indexed by rfid
            object_dict[rfid_value] = trigger
    return object_dict


def trigger_actions(trigger, transition_list, content_dict):
    """Trigger all of the actions specified by the database"""
    global old_content_thread
    if trigger in content_dict:
        content_film = choice(content_dict[trigger])
    else:
        content_film = choice(content_dict['default'])
    debug('Content:', content_film)
    # TODO: Get actual length of video (steal from video.py)
    duration = content_film['length']
    # start chart recorder
    start_chart(duration)
    # kill old film if necessary
    # try:
    while old_video_threads:
        thread = old_video_threads.pop()
        thread.stop()
    # except:
    #     pass
    # start films
    trans1_film = choice(transition_list)
    trans2_film = choice(transition_list)
    content_thread = videothread.VideoThread([trans1_film, content_film, trans2_film],
                                             media_dir=MEDIA_BASE, debug=DEBUG)
    content_thread.start()
    old_video_threads.append(content_thread)


def main():
    # setup everything
    report("Reading film database")
    film_list = read_film_file(MEDIA_BASE + '/' + FILMDB_FILE)
    debug("\nfilm_list", film_list)
    film_dict = create_film_lists_dict(film_list)
    debug(film_dict)
    content_dict = create_content_dict(film_dict['content'])
    debug("\ncontent_dict:", content_dict)
    object_dict = create_object_dict(film_dict["content"])
    debug("\nobject_dict:", object_dict, "\n")

    report("starting idle video")
    loop_film = choice(film_dict['loop'])
    loop_thread = videothread.VideoThread([loop_film], media_dir=MEDIA_BASE, debug=DEBUG)
    loop_thread.start()

    report("Setting up serial devices")
    setup_devices()
    # This is our main loop that listens and responds
    while 1:
        # check if all of our devices are active
        if not all_devices_live():
            setup_devices()
        # let's take actions if we can
        if all_critical_devices_live():
            rfid = listen_and_report()
            trigger = get_object_trigger(rfid, object_db)
            if trigger:
                trigger_actions(trigger, film_dict['transition'], content_dict)


def get_object_trigger(rfid, object_dict):
    if rfid not in object_dict:
        rfid = "default"
    return object_dict[rfid]


if __name__ == '__main__':
    try:
        # Enter the main loop
        main()
    except KeyboardInterrupt:
        nullin = open(os.devnull, 'r')
        nullout = open(os.devnull, 'w')
        call(["killall", "-9", "omxplayer", "omxplayer.bin"], stdout=nullout, stderr=nullout)
        nullin.close()
        nullout.close()
        report("")
        report("Exiting.")
