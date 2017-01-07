# test-report-rfid.py
# listen for RFID from active USB port
# author: SL Benz & Wes Modes
# created: 6 Jan 2017

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import serial
import os
import subprocess
import selenium.webdriver as webdriver
from selenium.webdriver.common.keys import Keys
from rfid_object_db import object_db

youtube_url = "https://www.youtube.com/embed/"
#youtube_url = "http://www.youtube.com/watch_popup?v="
#youtube_url = "https://www.youtube.com/tv#/watch?v="
#youtube_url = "https://www.youtube.com/watch?v="
youtube_post = "?rel=0&autoplay=1"

default_url = youtube_url + "OByCDlsk9jo" + youtube_post

rfid_send_count = 3
rfid_length = 43

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

# find active USB port
def get_active_usb():
    for port_num in range(10):
        usb_port = "/dev/ttyUSB" + str(port_num)
        print "Checking if %s is active:" % (usb_port),
        if os.path.exists(usb_port):
            print "Yes"
            return usb_port
        else:
            print "No"

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
    usb_port = get_active_usb()
    if not usb_port:
        print "ERROR: No active USB port found"
        exit()

    ser = serial.Serial(usb_port, 9600)

    print "Begin listening for RFID"
    # This is our main loop that listens and responds
    while 1 :
        # do we have data on the input buffer waiting
        if ser.in_waiting > 0:
            # if we send the same rfid multiple times
            #   in theory they should all be the same,
            #   but in practice we are sometimes missing bytes.
            #   Thus we send it multiple times to guard against data loss
            rfid_good = ""
            count = 0
            # we keep looking if we have something waiting
            #   AND we haven't exceeded our count
            #   AND we haven't already rec'd a good rfid
            while (ser.in_waiting > 0 and count < rfid_send_count and 
                   not rfid_good):
                rfid_in = ser.readline().strip()
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
            ser.reset_input_buffer()

            print "Begin listening for RFID"


if __name__ == "__main__":
    main()
