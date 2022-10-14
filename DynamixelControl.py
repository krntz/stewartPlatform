from dynamixel_sdk import *                    # Uses Dynamixel SDK library
import math

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
        self.ADDR_MX_MOVING_STATUS          = 46
        
        # Data Byte Length
        self.LEN_MX_GOAL_POSITION           = 4
        self.LEN_MX_PRESENT_POSITION        = 2
        
        # Values
        self.TORQUE_ENABLE                  = 1                 # Value for enabling the torque
        self.TORQUE_DISABLE                 = 0                 # Value for disabling the torque
        self.DXL_MINIMUM_POSITION_VALUE     = 204
        self.DXL_MAXIMUM_POSITION_VALUE     = 820
        self.DXL_DEGREES_PER_STEP           = 0.29              # Value for converting between servo steps and degrees
                                                                # TODO: This being a float means the movements will always be slightly off
                                                                #           - The servos cannot move fractions of steps
                                                                #           - Check if the error is large enough to matter and if there some way to fix it

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
        self.reset_servos()

        # Disable Torque
        for i in self.DXL_ids:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, i, self.ADDR_MX_TORQUE_ENABLE, self.TORQUE_DISABLE)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        # Close port
        self.portHandler.closePort()

    def reset_servos(self):
        """Sets servos back to 0 degrees rotation
        """

        if self.VERBOSE:
            print("Reseting servos to start position")

        gp = [{"id" : i, "position" : 512} for i in self.DXL_ids]

        self.sync_write(gp)

        while 1:
            moving = self.get_moving_status()
            if not all(moving):
                break

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
        # TODO: make this not hardcoded to odd and even servos
        for i,j in enumerate(goal_positions):
            if j["id"] % 2 != 0:
                goal_positions[i]["position"] = 1024 - j["position"]

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
                print("Sending %d to Dynamixel Servo #%d" % (i["position"], i["id"]))
            if dxl_addparam_result != True:
                raise Exception("[ID:%03d] groupSyncWrite addparam failed" % i["id"])
    
        # Syncwrite goal position
        dxl_comm_result = groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
    
        # Clear syncwrite parameter storage
        groupSyncWrite.clearParam()

    def get_current_positions(self):
        """Queries connected servos for their current positions.

        Returns
        -------
        current_positions : list of dicts
            Ids of servos and their respective current positions
        """
        current_positions = []

        for i in self.DXL_ids:
            dxl_current_position, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, i, self.ADDR_MX_PRESENT_POSITION)

            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

            current_positions.append({"id": i, "position" : dxl_current_position})

        return current_positions

    def move_degrees(self, degrees):
        """Moves connected servos by indicated number of degrees.

        Parameters
        ----------
        degrees : list of dicts, mandatory
            Ids of servos and the degrees to rotate them
        """

        current_positions = self.get_current_positions()

        goal_positions = [{"id" : j["id"], "position" : int(j["degrees"] / self.DXL_DEGREES_PER_STEP) + 512} for i,j in enumerate(degrees)]
        
        self.sync_write(goal_positions)

    def get_moving_status(self):
        moving_status = []

        for i in self.DXL_ids:
            dxl_moving_status, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, i, self.ADDR_MX_MOVING_STATUS)

            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

            moving_status.append(dxl_moving_status)

        return moving_status
