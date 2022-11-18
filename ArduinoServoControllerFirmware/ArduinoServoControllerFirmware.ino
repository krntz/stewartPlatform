#include <Servo.h>

enum commands {R, W};

const int s1Pin = 1;
const int s2Pin = 2;
const int s3Pin = 3;
const int s4Pin = 4;
const int s5Pin = 5;
const int s6Pin = 6;

const int baudrate = 1000000;

Servo s1;
Servo s2;
Servo s3;
Servo s4;
Servo s5;
Servo s6;

void setup() {
  //TODO:
  // - Would be great to do this dynamically
  // - - maybe require setting up the servos over serial?

  s1.attach(s1Pin);
  s2.attach(s2Pin);
  s3.attach(s3Pin);
  s4.attach(s4Pin);
  s5.attach(s5Pin);
  s6.attach(s6Pin);

  Serial.begin(baudrate);
}

void loop() {
  if (Serial.available()) {
    inByte = Serial.readBytesUntil('\n');

  // data packet
  // <command> <servoId> [position] \n

  switch (command) {
    case W:
      writeServoPosition();
      break;
    case R:
      readServoPosition();
      Serial.write();
      break;
  }
  }
}

int readServoPosition(int servoId) {
  // returns the current position of servo with id servoId

  return;
}

int writeServoPosition(int servoId) {
  // writes new position to servo

  return;
}