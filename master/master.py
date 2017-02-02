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
from time import sleep, time
import threading

# Constants
#
usb_port_prefix = "/dev/ttyUSB"
max_usb_ports = 12
rfid_send_count = 3
rfid_length = 43
max_retries = 20
retry_delay = 0.5
serial_timeout = 0.5

# communication protocols
req_id = "id"
req_start = "start"
req_stop = "stop"
rsp_ack = "ack"
req_handshake =  "hello?"
rsp_handshake =  "hello!"

# id's
id_rfid = "id:rfid"
id_chart = "id:chart"

# Globals
#

last_report_time = int(time())

# serial device handles
devices = {'rfid': {'name':     'RFID Reader',
                    'id':       'id:rfid',
                    'status':   'init',
                    'port':     ''
                    }, 
          'chart': {'name':     'Chart Recorder',
                    'id':       'id:chart',
                    'status':   'init',
                    'port':     ''
                    }
           }

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

#
# Device locating and setup
#

def is_port_active(port):
    """Check if given port is active"""
    if (port):
        #print "Checking if %s is active:" % (port)
        # we use a system call to see if this serial handle exists
        return os.path.exists(port)

def get_active_usb_ports():
    """Search usb ports and find out which ones are active, returning a list"""
    usb_list = []
    # we look for up to max_ports usb ports
    for port_num in range(max_usb_ports):
        usb_port = usb_port_prefix + str(port_num)
        if is_port_active(usb_port):
            usb_list.append(usb_port)
    return usb_list

def request_id(port):
    """Send an ID request to a serial port and return the ID we get"""
    # set up a serial port temporarily
    ser = serial.Serial(port, 9600, timeout=serial_timeout)
    # clear the buffers - TODO: Does this actually do it?
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    # we ask several times until we get an answer
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
    """Set up all of our serial ports connected to our devices"""
    print "Checking for active ports"
    usb_ports = get_active_usb_ports()
    if not usb_ports:
        print "ERROR: No active USB port found"
    for port in usb_ports:
        print "Setting up:", port,
        response = request_id(port)
        print "Response:", response,
        #
        # look through our list of expected devices
        for device in devices:
            # if device IDs as this device
            if (devices[device]['id'] in response):
                # asign a serial handle
                devices[device]['handle'] = serial.Serial(port, 9600, timeout=.5)
                # assign the port name
                devices[device]['port'] = port
                # mark is as currently live
                devices[device]['status'] = 'live'
                # print the name to console
                print devices[device]['name']
                # we don't need to look through the rest
                break
            # if device IDs as anything else
            else:
                print "Unknown"

def check_if_all_devices_live():
    global last_report_time
    for device in devices:
        if not is_port_active(devices[device]['port']):
            #devices['chart']['live'] = False
            # every 10 seconds, we report this
            if (int(time()) > last_report_time+10):
                print "WARNING: No %s found." % devices[device]['name']
                last_report_time = int(time())
            devices[device]['status'] == 'missing'
            device_missing = True

#
# device communication
#

def tell_device(device, text):
    ser = devices[device]['handle']
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
    """Start the chart recorder and set callback timer to turn it off"""
    global chart_timer
    # first we cancel any timer we've set before
    if (chart_timer):
        chart_timer.cancel()
        print "Canceling old timer"
    results = tell_device('chart', req_start)
    print "Start chart recorder sez:", results
    chart_timer = threading.Timer(time, stop_chart).start()

def stop_chart():
    """Stops the chart recorder"""
    results = tell_device('chart', req_stop)
    print "Stop chart recorder sez:", results

def trigger_actions(data):
    """Trigger all of the actions specified by the database"""
    duration = data["duration"]
    start_chart(duration)

def main():
    setup_serial()
    # This is our main loop that listens and responds
    while 1 :
        # check if all of our devices are active
        all_live = check_if_all_devices_live()
        if (not all_live):
            setup_serial()
        # we can proceed as long as the rfid device is active
        if (devices['rfid']['status'] == 'live'):
            rfid_device = devices['rfid']['handle']
            # do we have data on the input buffer waiting
            if rfid_device.in_waiting > 0:
                # if we send the same rfid multiple times
                #   in theory they should all be the same,
                #   but in practice we are sometimes missing bytes.
                #   Thus we send it multiple times to guard against data loss
                rfid_good = ""
                count = 0
                # we keep looking if we have something waiting
                #   AND we haven't exceeded our count
                #   AND we haven't already rec'd a good rfid
                while (rfid_device.in_waiting > 0 and count < rfid_send_count and 
                       not rfid_good):
                    rfid_in = rfid_device.readline().strip()
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
                rfid_device.reset_input_buffer()
                print "Continue listening for RFID"


if __name__=='__main__':
    # try:     
        # Enter the main loop
    main()
    # except Exception as e: 
    #     print ""
    #     print str(e)
    # except:
    #     print ""
    #     print "Exiting."
