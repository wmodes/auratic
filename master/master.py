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
import threading

# Constants
#
rfid_send_count = 3
rfid_length = 43
max_retries = 20
retry_delay = 0.5
serial_timeout = 0.5

# communication protocols
req_id = "id"
req_start = "start";
req_stop = "stop";
rsp_ack = "ack";

# id's
id_rfid = "id:rfid"
id_chart = "id:chart"

# serial device handles
rfid_serial = ""
chart_serial = ""

# timers
chart_timer = ""

# setup stuff
#
# print "Opening browser window. This will take a little bit."
# os.environ["DISPLAY"] = ":0.0"
# fp = webdriver.FirefoxProfile()
# fp.set_preference("browser.fullscreen.autohide",True)
# fp.set_preference("browser.fullscreen.animateUp",0)
# browser = webdriver.Firefox(firefox_profile=fp)
# browser.maximize_window()
# #browser.driver.manage().window().fullscreen()
# browser.get(default_url)

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

def request_id(port):
    """Send an ID request to the serial and return the ID we get"""
    ser = serial.Serial(port, 9600, timeout=serial_timeout)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    for i in range(max_retries):
        ser.write(req_id)
        sleep(retry_delay)
        waiting = ser.inWaiting()
        response = ser.readline().strip()
        # print "Serial Try", i, "=", response, "waiting:", waiting
        if response:
            break
        sleep(retry_delay)
    return response

def setup_serial():
    global rfid_serial, chart_serial
    usb_ports = get_active_usb_ports()
    if not usb_ports:
        print "ERROR: No active USB port found"
        exit()
    for port in usb_ports:
        print "Setting up:", port,
        response = request_id(port)
        print "Response:", response,
        if (id_rfid in response):
            rfid_serial = serial.Serial(port, 9600, timeout=.5)
            print "RFID Reader"
        elif (id_chart in response):
            chart_serial = serial.Serial(port, 9600, timeout=.5)
            print "Chart recorder"
        else:
            print "Unknown"

def tell_client(ser, text):
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    for i in range(max_retries):
        ser.write(text)
        sleep(retry_delay)
        waiting = ser.inWaiting()
        response = ser.readline().strip()
        # print "Serial Try", i, "=", response, "waiting:", waiting
        if rsp_ack in response:
            return response
        sleep(retry_delay)

def get_rfid_data(rfid):
    if rfid not in object_db:
        rfid = "default"
    return object_db[rfid]

def display_found_object(data):
    title = data["title"]
    category = data["category"]
    url = youtube_url + data["video"] + youtube_post
    print "This is a", title
    print "Showing video", url
    # browser.get(url)

def start_chart(time):
    global chart_timer
    """Start the chart recorder and set callback timer to turn it off"""
    global chart_timer
    # first we cancel any timer we've set before
    if (chart_timer):
        chart_timer.cancel()
    results = tell_client(chart_serial, req_start)
    print "Start chart recorder:", results
    chart_timer = threading.Timer(time, stop_chart).start()

def stop_chart():
    """Stops the chart recorder"""
    results = tell_client(chart_serial, req_stop)
    print "Stop chart recorder:", results

def trigger_actions(data):
    """Trigger all of the actions specified by the database"""
    duration = data["duration"]
    start_chart(duration)

def main():
    setup_serial()
    if not rfid_serial:
        print "FATAL ERROR: No RFID reader found."
        exit()
    if not chart_serial:
        print "WARNING: No chart reader found."

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
                data = get_rfid_data(rfid_good)
                display_found_object(data)
                trigger_actions(data)

            # clear incoming buffer in case we have stuff waiting
            rfid_serial.reset_input_buffer()

            print "Begin listening for RFID"


if __name__=='__main__':
    try:     
        # Enter the main loop
        main()
    except Exception as e: 
        print ""
        print str(e)
    except:
        print ""
        print "Exiting."
