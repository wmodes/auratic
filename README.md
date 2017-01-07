Truth Machine
=============
Part of a project for SL Benz' thesis project.

Hardward components include

- Raspberry Pi - serves as master and plays videos
- Arduino a - (slave) reads RFIDs and reports to Raspi
- Arduino b - (slave) controls chart reader 1
- Arduino c - (slave) controls chart reader 2

The C++ code is run on the Arduinos. The python code runs 
on the Pi.

RFID
----
The RFID is read by a Asiawill RDM6300 125Khz EM4100 RFID Reader 
Module UART Output Access Control System connected to an Arduino.
The Arduino is talking to the Pi via USB.

EM4100 specs have a 28 byte decimal code that looks something like:

    02:52:70:48:48:49:48:48:65:54:54:51:51:03:3

Chart Recorder
--------------
The slave Arduinos control a servo that swings a needle abck and forth
to emulate a chart recorder from an accelerometer or lie detector. 


