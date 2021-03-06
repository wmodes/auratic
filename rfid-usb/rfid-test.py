import string

from evdev import InputDevice
from select import select

DEVICE = "/dev/input/by-id/usb-Sycreader_RFID_Technology_Co.__Ltd_SYC_ID_IC_USB_Reader_08FF20140315-event-kbd"

# Modify as needed
scancodes = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r',
    20: u't', 21: u'y', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'\n', 29: u'LCTRL',
    30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'z', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n',
    50: u'm', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 57: u' ', 100: u'RALT'
}

keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
dev = InputDevice(DEVICE)

# while True:
#    r,w,x = select([dev], [], [])
#    for event in dev.read():
#         if event.type==1 and event.value==1:
#                 print( keys[ event.code ] )

id = ''
while True:
    r,w,x = select([dev], [], [])
    for event in dev.read():
        if event.type==1 and event.value==1:
            key = scancodes[event.code]
            if key != '\n':
                id += "%02d:" % int(key)
            else:
                id = id[0:-1]
                print "ID:", id
                id = ""

# while True:
#     r,w,x = select([dev], [], [])
#     #print "\nNew event.\n"
#     id = ""
#     key = ""
#     while (key != 'X'):
#         for event in dev.read():
#         event = dev.read_one()
#         if event.type==1 and event.value==1:
#             key = keys[ event.code ]
#             print key
#             id += "%02d:" % int(key)
#     print id

