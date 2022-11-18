#include <Servo.h>

enum commands {R, W};

const int baudrate = 1000000;

Servo servos[6];
const int pins[6] = {1, 2, 3, 4, 5, 6};

// splits a string at a separator
// taken from https://stackoverflow.com/a/14824108/7362882
String getValue(String data, char sep, int index) {
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == sep || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }

  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void setup() {
  //TODO:
  // - Would be great to do this dynamically
  // - - maybe require setting up the servos over serial?

  for (i = 0; i < 6; i++) {
    servos[i] = Servo;
    servos[i].attach(pins[i]);
  }

  Serial.begin(baudrate);
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readBytesUntil('\n');

    // data packet
    // <command> <servoId> [position] \n

    String command = getValue(data, ' ', 0);
    int servoId = getValue(data, ' ', 1).toInt();

    switch (command) {
      case W:
        int pos = getValue(data, ' ', 2).toInt();
        writeServoPosition(servoId, pos);
        break;
      case R:
        int pos = readServoPosition(servoId);
        Serial.write(pos);
        break;
      default:
        std::cout << "Unknown command" << std::endl;
    }
  }
}

int readServoPosition(int servoId) {
  // returns the current position of servo with id servoId

  return;
}

int writeServoPosition(int servoId, int pos) {
  // writes new position to servo

  return;
}