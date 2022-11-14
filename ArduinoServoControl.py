import serial

class ArduinoServoControl:
    def __init__(self,
                 verbose=False,
                 baudrate=1000000,
                 deviceName="dev/tty."):

        arduino = serial.Serial(deviceName, baudrate)
