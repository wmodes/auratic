import string

from evdev import InputDevice
from select import select

DEVICE = "/dev/input/by-id/usb-Sycreader_RFID_Technology_Co.__Ltd_SYC_ID_IC_USB_Reader_08FF20140315-event-kbd"

keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
dev = InputDevice(DEVICE)

while True:
   r,w,x = select([dev], [], [])
   for event in dev.read():
        if event.type==1 and event.value==1:
                print( keys[ event.code ] )

