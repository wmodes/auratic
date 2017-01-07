/*
  Pen.h - Library for Simulated Chart Recorder.
  Created by Wes Modes 4 December 2016
  Released into the public domain.
*/

#ifndef Pen_h
#define Pen_h

#include <Servo.h>
#include "Arduino.h"

class Pen 
{
  private:
        Servo _myservo;      // create servo object to control a servo
    int _pos, _dir, _spd, _amp, _pin; // see descriptions in constructor
    bool _comingHome; // tracks whether starting or ending movement
  public:
    Pen(int pin);       // This is the constructor
    bool traveling = false;
    void reset();
    void set(int, int, int);
    void move();
    void start(int, int);
    void position(int);
    void status();
};

#endif

