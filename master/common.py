#!/usr/bin/python
"""devices.py: listen for RFID from active USB port and trigger chart recorder and video
Author: Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)
Copyright: 2017, MIT"""

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from time import sleep, time

#
# Constants
#
DEBUG = 2

#
# Globals
#

# we only report each error periodically,
# so we keep a record of last report time
last_report_time = {}
# report interval in seconds
report_interval = 5

# we only report each DEBUG msg periodically,
# so we keep a record of last debug time
last_debug_time = {}
# report interval in seconds
debug_interval = 1


def report(*args):
    """immediately report information.
    Note: Accepts multiple arguments"""
    text = " ".join(list(map(str, args)))
    print text


def debug(text, level):
    if (DEBUG >= level):
        # if now is greater than our last debug time + an interval
        if (text not in last_debug_time or
                time() > last_debug_time[text] + debug_interval):
            report("debug: " + text)
            last_debug_time[text] = time()


def update(*args):
    """periodically report information at report_interval seconds.
    Note: Accepts multiple arguments"""
    text = " ".join(list(map(str, args)))
    # if now is greater than our last report time + an interval
    if (text not in last_report_time or
            time() > last_report_time[text] + report_interval):
        report(text)
        last_report_time[text] = time()
