#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""master.py: listen for RFID from active USB port and trigger chart recorder and video"""
__author__      = "Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)"
__copyright__   = "2017, MIT"

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import serial
import os
import subprocess
import selenium.webdriver as webdriver
from selenium.webdriver.common.keys import Keys
from rfid_object_db import *
from time import sleep

# Constants
#
rfid_send_count = 3
rfid_length = 43
id_req = "id"
id_response = "id:"
id_rfid = "id:rfid"
id_chart = "id:chart"

# setup stuff
#
print "Opening browser window. This will take about a minute."
os.environ["DISPLAY"] = ":0.0"
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.fullscreen.autohide",True)
fp.set_preference("browser.fullscreen.animateUp",0)
browser = webdriver.Firefox(firefox_profile=fp)
browser.maximize_window()
#browser.driver.manage().window().fullscreen()
browser.get(default_url)

def get_active_usb_ports():
    """Search usb ports and find out which ones are active, returning a list"""
    usb_list = []
    for port_num in range(10):
        usb_port = "/dev/ttyUSB" + str(port_num)
        print "Checking if %s is active:" % (usb_port),
        if os.path.exists(usb_port):
            print "Yes"
            usb_list.append(usb_port)
        else:
            print "No"
    return usb_list

def request_id(serial_port):
    """Send an ID request to the serial on a port and return the ID we get"""
    ser = serial.Serial(serial_port, 9600, timeout=1)
    ser.write(id_req)
    ser.flush()
    sleep(1)
    response = ser.readline()
    return response

def setup_serial():
    global rfid_serial, chart_serial
    usb_ports = get_active_usb_ports()
    if not usb_ports:
        print "ERROR: No active USB port found"
        exit()
    for port in usb_ports:
        print "Examining:", port, ":",
        response = request_id(port)
        if (response == id_rfid):
            rfid_serial = serial.Serial(port, 9600, timeout=1)
            print "RFID Reader"
        elif (response == id_chart):
            chart_serial = serial.Serial(port, 9600, timeout=1)
            print "Chart recorder"
        else:
            print "Unknown"

def display_found_object(rfid):
    if rfid not in object_db:
        rfid = "default"
    my_object = object_db[rfid]
    title = object_db[rfid]["title"]
    category = object_db[rfid]["category"]
    url = youtube_url + object_db[rfid]["video"] + youtube_post
    print "This is a", title
    print "Showing video", url
    browser.get(url)

def main():
    setup_serial()

    print "Begin listening for RFID"
    # This is our main loop that listens and responds
    while 1 :
        # do we have data on the input buffer waiting
        if rfid_serial.in_waiting > 0:
            # if we send the same rfid multiple times
            #   in theory they should all be the same,
            #   but in practice we are sometimes missing bytes.
            #   Thus we send it multiple times to guard against data loss
            rfid_good = ""
            count = 0
            # we keep looking if we have something waiting
            #   AND we haven't exceeded our count
            #   AND we haven't already rec'd a good rfid
            while (rfid_serial.in_waiting > 0 and count < rfid_send_count and 
                   not rfid_good):
                rfid_in = rfid_serial.readline().strip()
                # if the rfid has the proper length,
                # we can trust it
                if len(rfid_in) == rfid_length:
                    rfid_good = rfid_in
                    print "    Received good RFID:", rfid_in
                    break
                else:
                    print "    Received bad RFID:", rfid_in

            if rfid_good:
                print "RFID found:", rfid_good
                display_found_object(rfid_good)

            # clear incoming buffer in case we have stuff waiting
            rfid_serial.reset_input_buffer()

            print "Begin listening for RFID"


if __name__ == "__main__":
    main()