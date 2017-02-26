/* rfid-reader.cpp - RFID Reader (Truth Machine Project)
 by Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)
 29 January 2017 
*/

#include <SoftwareSerial.h>

SoftwareSerial RFID(2, 3); // RX and TX

int digit;
int led = 13;
int rfidLen = 41;
int rfidByteCount = 14;
int rfidCount = 3;
unsigned long sameIdWaitTime = 30000;
int delayBetweenReads = 100;
int debug = 0;

String savedId = "";
unsigned long savedTime = 0;

String reqId = "id";
String rspId = "id:rfid";
String reqStatus = "status";
String rspAck = "OK";
String reqHandshake = "hello?";
String rspHandshake = "hello!";
String reqDebug = "debug";
String reqNoDebug = "nodebug";

void checkForRequests()
{
  // do we have a request from the master?
  if (Serial.available() > 0) 
  {
    // get request from USB port
    String reqMaster = Serial.readString();
    //Serial.print("We received: ");
    //Serial.println(reqMaster);
    //
    // did we receive a HANDSHAKE request?
    if (reqMaster.indexOf(reqHandshake) >= 0) {
      Serial.println(rspHandshake);
    }
    // did we receive an ID request?
    else if (reqMaster.indexOf(reqId) >= 0) {
      //Serial.print("We sent: ");
      Serial.println(rspId);
    }
    // did we receive a STATUS request?
    else if (reqMaster.indexOf(reqStatus) >= 0) {
      Serial.println(reqStatus + ":" + rspAck);
    }
    // did we receive a NODEBUG request?
    else if (reqMaster.indexOf(reqNoDebug) >= 0) {
      Serial.println(reqNoDebug + ":" + rspAck);
      debug = 0;
    }
    // did we receive a DEBUG request?
    else if (reqMaster.indexOf(reqDebug) >= 0) {
      Serial.println(reqDebug + ":" + rspAck);
      debug = 1;
    }
    else {
      Serial.println("Unknown-request:" + reqMaster);
    }    
  }
}

void doTheThings()
{
  // do we have a digit waiting?
  if (RFID.available() > 0) 
  {
    // create a string array to put our full RFID
    String fullId = "";
    // let's get 14 of them
    for(int i = 0; i < rfidByteCount; i++) {
      // read new digit
      int digit = RFID.read();
      // convert digit to 2 digit string with colon
      char numStr[3]; 
      if (i < rfidByteCount - 1) {
        sprintf(numStr, "%02d:", digit);
      }
      else {
        sprintf(numStr, "%02d", digit);
      }
      // append 2 digit string to fullId
      fullId += numStr;
      // check to make sure we have another digit waiting
      // if not, bounce!
      delay(10);
      if (RFID.available() == 0) {
        break;
      }
    }
    // Is this the same ID we got last time?
    if (debug) {
      Serial.print("debug: last: "); Serial.println(savedId);
      Serial.print("debug: this: "); Serial.println(fullId);
    }
    // Is our ID the same as last time?
    if ((fullId == savedId) && (millis() < (savedTime + sameIdWaitTime))) {
      if (debug) {
        Serial.println("debug: ids are the same and time's not up!");
        Serial.print("old: "); Serial.print(savedTime);
        Serial.print(" new: "); Serial.print(millis());
        Serial.print(" compared with: ");
        Serial.println(savedTime + sameIdWaitTime);
      }
    }
    else {
      // We send three times to guard against serial data loss
      for(int i = 0; i < rfidCount; i++) {
        Serial.println(fullId);
      }
      // Save this ID
      savedId = fullId;
      savedTime = millis();
      digitalWrite(led, HIGH);
      delay(250);
      digitalWrite(led, LOW);
      delay(250);
      delay(delayBetweenReads);
    }
    // Okay, now to make sure we don't rapid fire ids
    RFID.flush();
  }
}

void setup()
{
    RFID.begin(9600);    // start serial to RFID reader
    RFID.setTimeout(500);  // we'll wait a half sec
    Serial.begin(9600);  // start serial to PC 
    Serial.setTimeout(500);  // we'll wait a half sec
    pinMode(led, OUTPUT);
}

void loop()
{
  checkForRequests();
  doTheThings();
}
