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

String reqId = "id";
String rspId = "id:rfid";
String reqStatus = "status";
String rspAck = "OK";
String reqHandshake = "hello?";
String rspHandshake = "hello!";

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
    char fullId[rfidLen];
    fullId[0] = '\0';
    // Yes! Great, let's get 14 of them
    for(int i = 0; i < rfidByteCount; i++) {
      // read new digit
      int digit = RFID.read();
      // convert digit to 2 digit string with colon
      char numStr[2]; 
      sprintf(numStr, "%02d", digit);
      // append 2 digit string to fullId
      fullId[i*3] = numStr[0];
      fullId[(i*3)+1] = numStr[1];
      if (i < rfidByteCount) {
          fullId[(i*3)+2] = ':';
      }
      // check to make sure we have another digit waiting
      // if not, bounce!
      if (RFID.available() == 0) {
        break;
      }
      delay(10);
    }
    // We send three times to guard against serial data loss
    for(int i = 0; i < rfidCount; i++) {
      Serial.println(fullId);
    }
    digitalWrite(led, HIGH);
    delay(250);
    digitalWrite(led, LOW);
    delay(250);
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
