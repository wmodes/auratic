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

DEBUG = 1

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

# we only report each error periodically,
# so we keep a record of last report time
last_report_time = {}
# report interval in seconds
report_interval = 5

# serial device handles
devices = {'rfid': {'name':     'RFID Reader',
                    'id':       'id:rfid',
                    'fault':    'critical',
                    'status':   'init',
                    'port':     '',
                    'sort':     1
                    }, 
          'chart1': {'name':    'Chart Recorder 1',
                    'id':       'id:chart',
                    'fault':    'warn',
                    'status':   'init',
                    'port':     '',
                    'sort':     2
                    },
          'chart2': {'name':    'Chart Recorder 2',
                    'id':       'id:chart',
                    'fault':    'silent',
                    'status':   'init',
                    'port':     '',
                    'sort':     3
                    }
           }

assigned_ports = []

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
    """Check if given port is active. 
    Note if no part is passed, it returns False"""
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

def request_id_from_device(port):
    """Send an ID request to a serial port and return the ID we get"""
    # we only want to check port if it is still active
    if (is_port_active(port)):
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
    # otherwise return empty string
    return ""

def setup_serial():
    """Set up all of our serial ports connected to our devices"""
    #print "Checking for active ports"
    try:
        usb_ports = get_active_usb_ports()
        # pause a moment to make sure system has set up the serial ports we've found
        # sleep(1)        # needed?
        if not usb_ports:
            report_at_intervals("ERROR: No active devices found")
        for port in usb_ports:
            debug("setup_serial(): Active ports" + str(usb_ports), 1)
            # if this port isn't already assigned
            if (port not in assigned_ports):
                debug("setup_serial(): Unassigned port: " + port, 1)
                #
                # look through our list of expected devices
                for device in sorted(devices.values(), key=lambda x: x['sort']):
                    # if the device is not already live and
                    if (device['status'] != 'live'):
                        debug("setup_serial(): Unassigned device: " + device['name'], 1)
                        # if device IDs as this device
                        response = request_id_from_device(port)
                        debug("setup_serial(): Response: " + response, 1)
                        if (device['id'] in response):
                            print "Setting up %s, ID: %s, Port: %s" % (device['name'], 
                                    response, port)
                            # asign a serial handle
                            device['handle'] = serial.Serial(port, 9600, timeout=.5)
                            # assign the port name
                            device['port'] = port
                            # add port to our assigned port list
                            if port not in assigned_ports:
                                assigned_ports.append(port) 
                            # mark is as currently live
                            device['status'] = 'live'
                            # we don't need to look through the rest of the devices
                            break
            # we continue looking through the active ports
    except IOError:
        print "WARNING: Setup error, retrying"
        sleep(1)
        setup_serial()

def all_devices_live():
    """Check if each device handle is still valid.
    Note that a fault with some critical devices will pause 
    any further action, while others just generate a warning. 
    Still other devices are optional and will just silently fail."""
    devices_ok = True
    # we iterate over the list of possible devices
    for device in sorted(devices.values(), key=lambda x: x['sort']):
        # check if port is active. Note if we lost the port previously and it is empty
        # is_port_active() returns False
        if not is_port_active(device['port']):
            #devices['chart']['live'] = False
            if (device['fault'] == "critical"):
                # at intervals we report this
                report_at_intervals("CRITICAL: %s disconnected." % device['name'])
            elif (device['fault'] == "warn"):
                # at intervals we report this
                report_at_intervals("WARNING: %s disconnected." % device['name'])
            # set status for this device
            device['status'] == 'missing'
            # unassign port
            device['port'] == ''
            # remove port from our assigned port list
            if device['port'] in assigned_ports:
                assigned_ports.remove(device['port']) 
            devices_ok = False
    return devices_ok

def all_critical_devices_live():
    """Quick check if critical devices are live relies on side effects of check_if_all_devices_live()"""
    critical_ok = True
    for device in sorted(devices.values(), key=lambda x: x['sort']):
        if device['fault'] == 'critical' and device['status'] != 'live':
            critical_ok = False
            break
    return critical_ok

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

#
# Outside world actions & communication
#

def debug(text, level):
    if (DEBUG >= level):
        print text

def report_at_intervals(text):
    # if now is greater than our last report time + an interval
    if (text not in last_report_time or
            time() > last_report_time[text] + report_interval):
        print text
        last_report_time[text] = time()

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

def do_the_things():
    """Do our main loop actions, particularly listening to the
    RFID reader and triggering actions"""
    try:
        report_at_intervals("Listening for RFID")
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
    except IOError:
        print "WARNING: Lost RFID device"

def main():
    setup_serial()
    # This is our main loop that listens and responds
    while 1 :
        # check if all of our devices are active
        if not all_devices_live():
            setup_serial()
        # let's take actions if we can
        if all_critical_devices_live():
            do_the_things()


if __name__=='__main__':
    try:     
        # Enter the main loop
        main()
    except KeyboardInterrupt:
        print ""
        print "Exiting."
    # except Exception as e: 
    #     print ""
    #     print str(e)
    # except:

