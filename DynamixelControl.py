import sys, tty, termios
from dynamixel_sdk import *                    # Uses Dynamixel SDK library

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
def getch():
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

class DynamixelControl:
    def __init__(self, verbose, DXL_ids, baudrate=1000000, deviceName="/dev/tty.usbserial-FT66WMA5", protocol_version=1.0):
        # Default setting
        self.DXL_ids                     = DXL_ids

        self.verbose = verbose

        # Control table address
        self.ADDR_MX_TORQUE_ENABLE      = 24
        self.ADDR_MX_GOAL_POSITION      = 30
        self.ADDR_MX_PRESENT_POSITION   = 36
        
        # Data Byte Length
        self.LEN_MX_GOAL_POSITION       = 4
        self.LEN_MX_PRESENT_POSITION    = 2
        
        
        self.TORQUE_ENABLE               = 1                 # Value for enabling the torque
        self.TORQUE_DISABLE              = 0                 # Value for disabling the torque
        self.DXL_MINIMUM_POSITION_VALUE  = 204
        self.DXL_MAXIMUM_POSITION_VALUE  = 820
        self.DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold

        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.portHandler = PortHandler(deviceName)
        
        # Initialize PacketHandler instance
        # Set the protocol version
        # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
        self.packetHandler = PacketHandler(protocol_version)
        
        # Open port and set baudrate
        try:
            if not self.portHandler.openPort():
                raise Exception("Failed to open port")
        except Exception as e:
            print(e)
        else:
            if self.verbose:
                print("Succeeded to open port")
        
        try:
            if not self.portHandler.setBaudRate(baudrate):
                raise Exception("Failed to set baudrate")
        except Exception as e:
            print(e)
            self.portHandler.closePort()
        else:
            if self.verbose:
                print("Succeeded to set baudrate")

        # Enable Torque
        for i in self.DXL_ids:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, i, self.ADDR_MX_TORQUE_ENABLE, self.TORQUE_ENABLE)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            else:
                if self.verbose:
                    print("Dynamixel#%d has been successfully connected" % i)

    def sync_write(self, goal_position):
        """ Writes a goal position to multiple Dynamixel servos
    
        Parameters
        ----------
        goal_position : int, mandatory
            The goal position to move servos to
    
        Raises
        ----------
        TypeError
            If goal_position is not an int
    
        ValueError
            If goal_position is outside the range specified by DXL_MINIMUM_POSITION_VALUE and DXL_MAXIMUM_POSITION_VALUE
        """
    
        if goal_position is not int:
            raise TypeError("Goal position should be integer")
    
        if not (goal_position <= self.DXL_MAXIMUM_POSITION_VALUE && goal_position >= self.DXL_MINIMUM_POSITION_VALUE):
            raise ValueError("Goal position %03d may cause damage to platform" % goal_position)
    
        # Initialize GroupSyncWrite instance
        groupSyncWrite = GroupSyncWrite(self.portHandler, self.packetHandler, self.ADDR_MX_GOAL_POSITION, self.LEN_MX_GOAL_POSITION)
    
        # Add goal position value to the Syncwrite parameter storage
        for i in self.DXL_ids:
            if i % 2 != 0:
                goal_position = 1024 - goal_position
    
            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(goal_position)),
                                   DXL_HIBYTE(DXL_LOWORD(goal_position)),
                                   DXL_LOBYTE(DXL_HIWORD(goal_position)),
                                   DXL_HIBYTE(DXL_HIWORD(goal_position))]
            dxl_addparam_result = groupSyncWrite.addParam(i, param_goal_position)
            if dxl_addparam_result != True:
                raise Exception("[ID:%03d] groupSyncWrite addparam failed" % i)
    
        # Syncwrite goal position
        dxl_comm_result = groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
    
        # Clear syncwrite parameter storage
        groupSyncWrite.clearParam()
    
        # Wait until servos have stopped moving
        while 1:
            moving = []
            # Read present position
            for i in self.DXL_ids:
                dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, i, self.ADDR_MX_PRESENT_POSITION)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % self.packetHandler.getRxPacketError(dxl_error))
    
                moving.append(abs(dxl_goal_position[index] - dxl_present_position) > self.DXL_MOVING_STATUS_THRESHOLD)
    
            if not all(moving):
                break
    def __del__(self):
        # Disable Torque
        for i in DXL_ids:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))

        # Close port
        portHandler.closePort()

index = 0
dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]         # Goal position

while 1:
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        break

    # Allocate goal position value into byte array
    goal_position = dxl_goal_position[index]
    try:
        sync_write(goal_position, DXL_ids)
    except TypeError as te:
        print(te)
        portHandler.closePort()
    except ValueError as ve:
        print(ve)
        portHandler.closePort()
    except Exception as e:
        print(e)
        portHandler.closePort()

    # Change goal position
    if index == 0:
        index = 1
    else:
        index = 0
