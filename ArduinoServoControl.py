import serial

class ArduinoServoControl:
    def __init__(self,
                 verbose=False,
                 baudrate=1000000,
                 deviceName="dev/tty."):

        self.VERBOSE = verbose
        try:
            self.arduino = serial.Serial(deviceName, baudrate)
        except SerialException as se:
            print(se)
        except ValueError as ve:
            print(ve)
        else:
            if self.VERBOSE:
                print("Succeeded to open port to device " + deviceName)

    def __del__(self):
        self.arduino.close()

    def bulk_write(self, goal_positions):
        self.arduino.write(goal_positions)
