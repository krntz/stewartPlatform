from dynamixel_sdk import *                    # Uses Dynamixel SDK library

class DynamixelControl:
    def __init__(self,
                 DXL_ids, 
                 verbose=False,
                 baudrate=1000000, 
                 deviceName="/dev/tty.usbserial-FT66WMA5", 
                 protocol_version=1.0):

        self.DXL_ids                        = DXL_ids
        self.VERBOSE                        = verbose

        # Control table address
        self.ADDR_MX_TORQUE_ENABLE          = 24
        self.ADDR_MX_GOAL_POSITION          = 30
        self.ADDR_MX_PRESENT_POSITION       = 36
        self.ADDR_DXL_MOVING_STATYS         = 46
        
        # Data Byte Length
        self.LEN_MX_GOAL_POSITION           = 4
        self.LEN_MX_PRESENT_POSITION        = 2
        
        # Values
        self.TORQUE_ENABLE                  = 1                 # Value for enabling the torque
        self.TORQUE_DISABLE                 = 0                 # Value for disabling the torque
        self.DXL_MINIMUM_POSITION_VALUE     = 204
        self.DXL_MAXIMUM_POSITION_VALUE     = 820
        self.DXL_MOVING_STATUS_THRESHOLD    = 20                # Dynamixel moving status threshold

        # Initialize PortHandler instance
        self.portHandler = PortHandler(deviceName)
        
        # Initialize PacketHandler instance
        self.packetHandler = PacketHandler(protocol_version)
        
        # Open port and set baudrate
        try:
            if not self.portHandler.openPort():
                raise Exception("Failed to open port")
        except Exception as e:
            print(e)
        else:
            if self.VERBOSE:
                print("Succeeded to open port")
        
        try:
            if not self.portHandler.setBaudRate(baudrate):
                raise Exception("Failed to set baudrate")
        except Exception as e:
            print(e)
            self.portHandler.closePort()
        else:
            if self.VERBOSE:
                print("Succeeded to set baudrate")

        # Enable Torque
        for i in self.DXL_ids:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, i, self.ADDR_MX_TORQUE_ENABLE, self.TORQUE_ENABLE)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            else:
                if self.VERBOSE:
                    print("Dynamixel#%d has been successfully connected" % i)

    def __del__(self):
        # Disable Torque
        for i in self.DXL_ids:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, i, self.ADDR_MX_TORQUE_ENABLE, self.TORQUE_DISABLE)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        # Close port
        self.portHandler.closePort()

    def sync_write(self, goal_positions):
        """ Writes a goal position to multiple Dynamixel servos
    
        Parameters
        ----------
        goal_positions : list of dicts, mandatory
            Ids of servos and their respective goal positions to move to
    
        Raises
        ----------
        ValueError
            If a goal position is outside the range specified by DXL_MINIMUM_POSITION_VALUE and DXL_MAXIMUM_POSITION_VALUE

        Exception
            If adding positions to groupSyncWrite fails
        """
    
    
        # Initialize GroupSyncWrite instance
        groupSyncWrite = GroupSyncWrite(self.portHandler, self.packetHandler, self.ADDR_MX_GOAL_POSITION, self.LEN_MX_GOAL_POSITION)
    
        # Add goal position value to the Syncwrite parameter storage
        for i in goal_positions:
            if not (i["position"] <= self.DXL_MAXIMUM_POSITION_VALUE and i["position"] >= self.DXL_MINIMUM_POSITION_VALUE):
                raise ValueError("Goal position %d may cause damage to platform" % i["position"])

            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(i["position"])),
                                   DXL_HIBYTE(DXL_LOWORD(i["position"])),
                                   DXL_LOBYTE(DXL_HIWORD(i["position"])),
                                   DXL_HIBYTE(DXL_HIWORD(i["position"]))]
            dxl_addparam_result = groupSyncWrite.addParam(i["id"], param_goal_position)
            if self.VERBOSE:
                print("Sending %d to Dynamixel Servo #%d" % (gp, i["id"]))
            if dxl_addparam_result != True:
                raise Exception("[ID:%03d] groupSyncWrite addparam failed" % i["id"])
    
        # Syncwrite goal position
        dxl_comm_result = groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
    
        # Clear syncwrite parameter storage
        groupSyncWrite.clearParam()

    def get_moving_status(self, servoID):
        # Wait until servos have stopped moving

        dxl_moving_status, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, servoID, 46)

        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        return dxl_moving_status
