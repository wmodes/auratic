#!/usr/bin/python
"""master.py: listen for RFID from active USB port and trigger chart recorder and video
Author: Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)
Copyright: 2017, MIT"""

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from devices import *
from video import *


def trigger_actions(data):
    """Trigger all of the actions specified by the database"""
    # get trigger
    trigger = data["trigger"]
    if trigger in content_film_dict:
        content_film = choice(content_film_dict[trigger])
    else:
        content_film = content_film_dict['default']
    duration = content_film["length"]
    # start chart recorder
    start_chart(duration)
    # start films
    trans1_film = choice(transition_film_list)
    trans2_film = choice(transition_film_list)
    content = videothread.VideoThread([trans1_film, content_film, trans2_film], debug=1)

def main():
    report("Reading film database")
    create_film_lists()
    create_content_dict()

    report("starting idle video")
    loop_film = choice(loop_film_list)
    loop = videothread.VideoThread([loop_film], debug=1)

    report("Setting up serial devices")
    setup_serial()
    # This is our main loop that listens and responds
    while 1:
        # check if all of our devices are active
        if not all_devices_live():
            setup_serial()
        # let's take actions if we can
        if all_critical_devices_live():
            object_data = listen_and_report()
            if object_data:
                trigger_actions(object_data)


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