#!/usr/bin/python
"""devices.py: listen for RFID from active USB port and trigger chart recorder and video
Author: Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)
Copyright: 2017, MIT"""

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import serial
import os
import subprocess
import selenium.webdriver as webdriver
from selenium.webdriver.common.keys import Keys
from rfid_object_db import *
from time import sleep, time
import threading

from common import *

# Constants
#
DEBUG = 2
USB_PORT_PREFIX = "/dev/ttyUSB"
MAX_USB_PORTS = 12
RFID_SEND_COUNT = 3
RFID_LENGTH = 41
MAX_RETRIES = 20
RETRY_DELAY = 0.5
SERIAL_TIMEOUT = 0.5

# communication protocols
REQ_ID = "id"
REQ_START = "start"
REQ_STOP = "stop"
RSP_ACK = "OK"
REQ_HANDSHAKE = "hello?"
RSP_HANDSHAKE = "hello!"

# id's
ID_RFID = "id:rfid"
ID_CHART = "id:chart"

#
# Globals
#

# serial device handles
devices = {'rfid': {'key':      'rfid',
                    'name':     'RFID Reader',
                    'id':       'id:rfid',
                    'fault':    'critical',
                    'status':   'init',
                    'port':     '/dev/input/by-id/usb-Sycreader_RFID_Technology_Co.__Ltd_SYC_ID_IC_USB_Reader_08FF20140315-event-kbd',
                    'port-status': 'fixed',
                    'sort':     1
                    },
           'chart1': {'key':     'chart1',
                      'name':    'Chart Recorder 1',
                      'id':       'id:chart',
                      'fault':    'warn',
                      'status':   'init',
                      'port':     '',
                      'port-status': 'variable',
                      'sort':     2
                      },
           'chart2': {'key':      'chart2',
                      'name':     'Chart Recorder 2',
                      'id':       'id:chart',
                      'fault':    'silent',
                      'status':   'init',
                      'port':     '',
                      'port-status': 'variable',
                      'sort':     3
                      }
           }

assigned_ports = []

# timers
chart_timer = ""


#
# Device locating and setup
#

def sorted_devices():
    """Return list of devices sorted by sort order values in devices dictionary"""
    return sorted(devices.values(), key=lambda x: x['sort'])


def is_port_active(port):
    """Check if given port is active.
    Note if no part is passed, it returns False"""
    if (port):
        # report("Checking if %s is active:" % (port))
        # we use a system call to see if this serial handle exists
        return os.path.exists(port)


def get_active_usb_ports():
    """Search usb ports and find out which ones are active, returning a list"""
    usb_list = []
    # we look for up to max_ports usb ports
    for port_num in range(MAX_USB_PORTS):
        usb_port = USB_PORT_PREFIX + str(port_num)
        if is_port_active(usb_port):
            usb_list.append(usb_port)
    return usb_list


def request_id_from_device(port):
    """Send an ID request to a serial port and return the ID we get"""
    # we only want to check port if it is still active
    if (is_port_active(port)):
        # set up a serial port temporarily
        ser = serial.Serial(port, 9600, timeout=SERIAL_TIMEOUT)
        # clear the buffers - TODO: Does this actually do it?
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        # we ask several times until we get an answer
        for i in range(MAX_RETRIES):
            ser.write(REQ_ID)
            sleep(RETRY_DELAY)
            waiting = ser.inWaiting()
            response = ser.readline().strip()
            # report("Serial Try", i, "=", response, "waiting:", waiting)
            if response:
                break
            sleep(RETRY_DELAY)
        return response
    # otherwise return empty string
    return ""


def setup_serial():
    """Set up all of our serial ports connected to our devices"""
    # report("Checking for active ports")
    try:
        usb_ports = get_active_usb_ports()
        # First we assign all of our fixed port devices
        for device in sorted_devices():
            if (device['port-status'] == 'fixed' and not is_port_active(device['port'])):
                debug("setup_serial(): Unassigned device: " + device['name'], 1)
                report("Setting up %s, ID: %s, Port: %s" % (device['name'],
                                                            response, port))
                # asign a serial handle
                device['handle'] = serial.Serial(port, 9600, timeout=.5)
                # add port to our assigned port list
                if port not in assigned_ports:
                    assigned_ports.append(port)
                # mark is as currently live
                device['status'] = 'live'
        # Now we assign all of our variable port devices
        for port in usb_ports:
            debug("setup_serial(): Active ports: " + str(usb_ports), 1)
            debug("setup_serial(): Registered ports: " + str(assigned_ports), 1)
            # if this port isn't already assigned
            if (port not in assigned_ports):
                debug("setup_serial(): Unassigned port: " + port, 1)
                #
                # look through our list of expected devices
                for device in sorted_devices():
                    # if the device is not fixed port and not already live
                    if (device['port-status'] != 'fixed' and not is_port_active(device['port'])):
                        debug("setup_serial(): Unassigned device: " + device['name'], 1)
                        # if device IDs as this device
                        response = request_id_from_device(port)
                        debug("setup_serial(): Response: " + response, 1)
                        if (device['id'] in response):
                            report("Setting up %s, ID: %s, Port: %s" % (device['name'],
                                                                        response, port))
                            # asign a serial handle
                            device['handle'] = serial.Serial(port, 9600, timeout=.5)
                            # assign the port name
                            device['port'] = port
                            # add port to our assigned port list
                            if port not in assigned_ports:
                                assigned_ports.append(port)
                            # mark is as currently live
                            device['status'] = 'live'
                            # we don't need to look through the rest of the
                            # devices
                            break
            # we continue looking through the active ports
    except IOError:
        report("WARNING: Setup error, retrying")
        sleep(1)
        setup_serial()


def all_devices_live():
    """Check if each device handle is still valid.
    Note that a fault with some critical devices will pause
    any further action, while others just generate a warning.
    Still other devices are optional and will just silently fail."""
    devices_ok = True
    # we iterate over the list of possible devices
    for device in sorted_devices():
        # check if port is active. Note if we lost the port previously and it is empty
        # is_port_active() returns False
        if not is_port_active(device['port']):
            # devices['chart']['live'] = False
            if (device['fault'] == 'critical'):
                # at intervals we report this
                update("CRITICAL: %s disconnected." % device['name'])
            elif (device['fault'] == 'warn'):
                # at intervals we report this
                update("WARNING: %s disconnected." % device['name'])
            # set status for this device
            device['status'] == 'missing'
            # unassign port
            if device['port-status'] != "fixed":
                device['port'] == ''
                # remove port from our assigned port list
                if device['port'] in assigned_ports:
                    assigned_ports.remove(device['port'])
            devices_ok = False
    return devices_ok


def all_critical_devices_live():
    """Quick check if critical devices are live relies on side effects of check_if_all_devices_live()"""
    critical_ok = True
    for device in sorted_devices():
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
    for i in range(MAX_RETRIES):
        ser.write(text)
        sleep(RETRY_DELAY)
        waiting = ser.inWaiting()
        response = ser.readline().strip()
        # report("Serial Try", i, "=", response, "waiting:", waiting)
        if RSP_ACK in response:
            return response
        sleep(RETRY_DELAY)


def get_rfid_data(rfid):
    if rfid not in object_db:
        rfid = "default"
    return object_db[rfid]

#
# Outside world actions & communication
#

def display_found_object(data):
    title = data["title"]
    category = data["category"]
    url = youtube_url + data["video"] + youtube_post
    report("This is a", title)
    report("Showing video", url)
    # browser.get(url)


def start_chart(time):
    """Start chart recorders and set callback timer to turn it off"""
    global chart_timer
    # first we cancel any timer we've set before
    if (chart_timer):
        chart_timer.cancel()
        report("Canceling old timer")
    # tell every connected chart recorder to start
    for device in sorted_devices():
        if 'chart' in device['key'] and is_port_active(device['port']):
            results = tell_device(device['key'], REQ_START)
            report("Starting %s. It responds: %s" % (device['name'], results))
    chart_timer = threading.Timer(time, stop_chart).start()


def stop_chart():
    """Stops chart recorders"""
    for device in sorted_devices():
        if 'chart' in device['key'] and is_port_active(device['port']):
            results = tell_device(device['key'], REQ_STOP)
            report("Stopping %s. It responds: %s" % (device['name'], results))


def listen_and_report():
    """Do our main loop actions, particularly listening to the
    RFID reader and triggering actions"""
    result = None
    try:
        update("Listening for RFID")
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
            while (rfid_device.in_waiting > 0 and count < RFID_SEND_COUNT and
                   not rfid_good):
                rfid_in = rfid_device.readline().strip()
                # if the rfid has the proper length,
                # we can trust it
                if len(rfid_in) == RFID_LENGTH:
                    rfid_good = rfid_in
                    report("    Received good RFID:", rfid_in)
                else:
                    report("    Received bad RFID:", rfid_in)
            if rfid_good:
                report("RFID found:", rfid_good)
                result = get_rfid_data(rfid_good)
            # clear incoming buffer in case we have stuff waiting
            rfid_device.reset_input_buffer()
            rfid_device.flushInput()
            report("Continue listening for RFID")
    except IOError:
        update("WARNING: Lost RFID device")
    return(result)


def main():
    setup_serial()
    # This is our main loop that listens and responds
    while 1:
        # check if all of our devices are active
        if not all_devices_live():
            setup_serial()
        # let's take actions if we can
        if all_critical_devices_live():
            listen_and_report()


if __name__ == '__main__':
    try:
        # Enter the main loop
        main()
    except KeyboardInterrupt:
        report("")
        report("Exiting.")
    # except Exception as e:
    #     print ""
    #     print str(e)
    # except:
