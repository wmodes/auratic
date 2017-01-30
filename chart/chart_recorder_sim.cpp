/* chart_recorder.cpp - Simulated Chart Recorder (Truth Machine Project)
 by Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)
 29 January 2017 
*/

#include <Servo.h>
#include <math.h>
using namespace std;

// CONSTANTS

const int PENMIN = 70;       // minimum alloable rotation of servo
const int PENMAX = 120;     // maximam allowable rotation of servo
const int PENAMP = (PENMAX - PENMIN) / 2; // max allowable amplitude
const int PENREST = PENMIN + PENAMP;  // where pen rests, center of min & max
const int PENPERIOD = 100;  // number of moves between start and end of full cycle
const int PENFREQ = 1;      // number of full waves to make in each cycle

const int GLOBAL_PERIOD = 500;
const int GLOBAL_WAIT = 10;

const int AVAILPENS[] = {9, 10, 11, 3, 5, 6};   // avail arduino pins (order of pref)
const int MAXPENS = sizeof(AVAILPENS);
const int PENSINUSE = 2;    // how many pens are we actually using

String req_id = "id";
String req_start = "start";
String req_stop = "stop";
String rsp_id = "id:chart";
String rsp_ack = "ack";

// Globals
boolean activated = false;

// Set up 

int penPos[PENSINUSE];      // postion of servo
int penX[PENSINUSE];        // graph position of x (vertical value)
int penPer[PENSINUSE];      // period of one wave
int penAmp[PENSINUSE];      // amplitude of current movement 0 to 100%
bool penMoving[PENSINUSE];  // check whether still traveling
Servo servo[PENSINUSE];     // declare an array of server objects
int datasetPos[PENSINUSE];  // records where we are in the dataset

// a sorta EKG dataset
int dataset0[] = {75, 65, 75, 100, 75, 100, 75, 50, 
  25, 25, 15, 15, 75, 10, 10, 5, 
  25, 10, 10, 10, 25, 10, 10, 10,
  25, 10, 10, 10, 25, 10, 10, 10
};

// a sorta heartbeat dataset
int dataset1[] = {
  5, 5, 5, 5, 20, 100, 50, 
  5, 5, 5, 5, 5, 
  5, 5, 5, 5, 5, 
  5, 5, 5, 5, 5
};

int* dataset[] = {
  dataset0,
  dataset1
};

int datalength0 = sizeof(dataset0)/sizeof(*dataset0);
int datalength1 = sizeof(dataset1)/sizeof(*dataset1);

int datalength[] = {
  datalength0,
  datalength1
};

// // calculate length of array (sigh, C++)
// const int DATASIZE = sizeof(dataset)/sizeof(*dataset);

void penSetup(int penNo) {
  servo[penNo].attach(AVAILPENS[penNo]);  // attaches the servo object to specified pin
  penReset(penNo);
}

void penStart(int penNo, int amp)
{
  penPos[penNo] = PENREST;
  penX[penNo] = 0;
  penPer[penNo] = PENPERIOD * amp / 100;
  penAmp[penNo] = amp;
  penMoving[penNo] = true;
  penPosition(penNo, PENREST);
}

void penReset(int penNo)
{
  //Serial.println("RESETing!");
  penPos[penNo] = PENREST;
  penX[penNo] = 0;
  penPer[penNo] = 1;
  penAmp[penNo] = 0;
  penMoving[penNo] = false;
  //penStatus(penNo);
  //penPosition(penNo, penPos[penNo]);
  //Serial.println("Done RESETing!");
}

void penMove(int penNo)
{
  // if we aren't traveling, we shouldn't be moving
  if (! penMoving[penNo]) 
  {
    // Serial.println("Done traveling");
    return;
  }

  double penY = sin(2 * (double) M_PI * PENFREQ * ((double) penX[penNo] / PENPERIOD));
  int newPos = PENREST + (PENAMP * penY * penAmp[penNo] / 100);
  // check to make sure pen hasn't hit our limits (not likely, but a good practice)
  if (newPos > PENMAX) 
  {
    newPos = PENMAX;
  }
  else if (newPos < PENMIN) 
  {
    newPos = PENMIN;
  }
  // okay, we like our newPos, let's set it
  penPos[penNo] = newPos;
  // increment our X coordinate
  penX[penNo]++;
  // are we at the end of the period?
  if (penX[penNo] > penPer[penNo]) 
  {
    penPos[penNo] = PENREST;
    penX[penNo] = 0;
    penPer[penNo] = 1;
    penAmp[penNo] = 0;
    penMoving[penNo] = false;
  }
  else 
  {
    // now move the actual servo
    penPosition(penNo, penPos[penNo]);
    // Serial.print(penX[penNo]);
    // Serial.print(", ");
    // Serial.print(penY);
    // Serial.print(", position: ");
    // Serial.println(penPos[penNo]);
    // Serial.print(".");
  }
}

void penPosition(int penNo, int pos)
{
  servo[penNo].write(pos);
}

void penStatus(int penNo)
{
  Serial.print("Pen: ");
  Serial.print(penNo);
  Serial.print(" on pin: ");
  Serial.println(AVAILPENS[penNo]);

  Serial.print("Period: ");
  Serial.print(penPer[penNo]);
  Serial.print(", Amplitude: ");
  Serial.println(penAmp[penNo]);

  Serial.print("Position: ");
  Serial.print(penPos[penNo]);
  Serial.print(", PenX: ");
  Serial.print(penX[penNo]);
  Serial.print(", Pen moving: ");
  Serial.println(penMoving[penNo]);
  Serial.println("");
}

void moveAll() 
{
  for (int penNo = 0; penNo < PENSINUSE; penNo += 1) {
    penMove(penNo);
  }
  delay(GLOBAL_WAIT);
}


void setup() 
{
  Serial.begin(9600);      // open the serial port at 9600 bps:
  //Serial.println("\n\n\n");
  for (int penNo = 0; penNo < PENSINUSE; penNo += 1) {
    penSetup(penNo);
    datasetPos[penNo] = 0;
  }
  delay(2000);
}

int find_text(String needle, String haystack) {
  int foundpos = -1;
  for (int i = 0; i <= haystack.length() - needle.length(); i++) {
    if (haystack.substring(i,needle.length()+i) == needle) {
      foundpos = i;
    }
  }
  return foundpos;
}

void loop() 
{
  // do we have a request from the master?
  if (Serial.available() > 0) 
  {
    String master_req = Serial.readString();
    //Serial.print("We received: ");
    //Serial.println(master_req);
    if (find_text(req_id, master_req) >= 0) {
      //Serial.print("We sent: ");
      Serial.println(rsp_id);
    }
    else if (find_text(req_start, master_req) >= 0) {
      Serial.println(req_start + rsp_ack);
      activated = true;
    }
    else if (find_text(req_stop, master_req) >= 0) {
      Serial.println(req_stop + rsp_ack);
      activated = false;
    }
  }
  if (activated) {
    // for each attached pen, we update it once per cycle
    for (int penNo = 0; penNo < PENSINUSE; penNo += 1) {
      //penStatus(penNo);
      // if we are not in the middle of a wave...
      if (! penMoving[penNo]){
        // ... get a new wave from the dataset
        int newAmp = dataset[penNo][datasetPos[penNo]];
        // Serial.print("Dataset Pos: ");
        // Serial.print(datasetPos[penNo]);
        // Serial.print(", New Amp: ");
        // Serial.println(newAmp);
        penStart(penNo, newAmp);
        datasetPos[penNo]++;
        // check to see if we've run out of data
        if (datasetPos[penNo] >= datalength[penNo]) {
          datasetPos[penNo] = 0;
        }
        //penStatus(penNo);
      }
      else {
        penMove(penNo);
      }
    }
    delay(GLOBAL_WAIT);
  }
}

