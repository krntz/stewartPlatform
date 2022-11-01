# based on https://www.xarg.org/paper/inverse-kinematics-of-a-stewart-platform/ and https://github.com/Yeok-c/Stewart_Py

import numpy as np

class StewartPlatform:
    def __init__(self, 
                 radiusBase, 
                 radiusPlatform, 
                 servoHornLength, 
                 rodLength, 
                 anchorAngleBase, 
                 anchorAnglePlatform, 
                 platform_rot,
                 verbose=False):
        """Sets up a mathematical representation of the Stewart platform
        """
        self.radiusBase             = radiusBase            # Circumscribed radius of base
        self.radiusPlatform         = radiusPlatform        # Circumscribed radius of platform
        self.servoHornLength        = servoHornLength       # Distance between servo shaft and servo horn anchor
        self.rodLength              = rodLength             # Length of rod
        self.anchorAngleBase        = anchorAngleBase       # Half of angle between two anchors on the base
        self.anchorAnglePlatform    = anchorAnglePlatform   # Half of angle between two anchors on the platform
        self.platform_rot           = platform_rot          # Rotation of platform relative to the base

        if verbose:
            print("Using following parameters for mathematical model:")
            print("radiusBase: %d" % self.radiusBase)
            print("radiusPlatform: %d" % self.radiusPlatform)
            print("servoHornLength: %d" % self.servoHornLength)
            print("rodLength: %d" % self.rodLength)
            print("anchorAngleBase: %f" % self.anchorAngleBase)
            print("anchorAnglePlatform: %f" % self.anchorAnglePlatform)
            print("platform_rot: %d" % self.platform_rot)
            print()

        # offset rotation of servo shafts in radians
        # the hexagonal base is circumscribed with a circle, with each servo shaft being a single point on the circle
        # beta[i] denotes how far around the circle the servo shaft is
        self.servoOffsetRotation = np.array([np.pi/2 + np.pi, 
                                             np.pi/2,
                                             2*np.pi/3 + np.pi/2 + np.pi, 
                                             2*np.pi/3 + np.pi/2,
                                             4*np.pi/3 + np.pi/2 + np.pi, 
                                             4*np.pi/3 + np.pi/2])

        if verbose:
            print("---servoOffsetRotation---")
            print(self.servoOffsetRotation)
            print()

        # Calculate polar coordinates of attachment points on base (polarCoordsBase) and platform (polarCoordsPlatform)
        # Essentially distance from center of hexagonal base and rotation from an axis
        self.polarCoordsBase = np.array([-anchorAngleBase,
                                         anchorAngleBase,
                                         2*np.pi/3 - anchorAngleBase,
                                         2*np.pi/3 + anchorAngleBase,
                                         4*np.pi/3 - anchorAngleBase,
                                         4*np.pi/3 + anchorAngleBase])

        #self.polarCoordsBase = self.polarCoordsBase + np.repeat(self.platform_rot, 6)
        if verbose:
            print("---polarCoordsBase---")
            print(self.polarCoordsBase)
            print()

        self.polarCoordsPlatform = np.array([-anchorAnglePlatform,
                                             anchorAnglePlatform,
                                             2*np.pi/3 - anchorAnglePlatform,
                                             2*np.pi/3 + anchorAnglePlatform,
                                             4*np.pi/3 - anchorAnglePlatform,
                                             4*np.pi/3 + anchorAnglePlatform])

        #self.polarCoordsPlatform = self.polarCoordsPlatform + np.repeat(self.platform_rot, 6)

        if verbose:
            print("---polarCoordsPlatform---")
            print(self.polarCoordsPlatform)
            print()

        # Calculate cartesian coordinates of servo shafts

        # Base
        self.cartesianCoordsBase = radiusBase * np.array([[np.cos(x), np.sin(x), 0] for x in self.polarCoordsBase])
        self.cartesianCoordsBase = np.transpose(self.cartesianCoordsBase)

        if verbose:
            print("---cartesianCoordsBase---")
            print(self.cartesianCoordsBase)
            print()

        # Platform
        self.cartesianCoordsPlatform = radiusPlatform * np.array([[np.cos(x), np.sin(x), 0] for x in self.polarCoordsPlatform])
        self.cartesianCoordsPlatform = np.transpose(self.cartesianCoordsPlatform)

        if verbose:
            print("---cartesianCoordsPlatform---")
            print(self.cartesianCoordsPlatform)
            print()

        # Define home position of platform
        z = np.sqrt(self.rodLength**2 + self.servoHornLength**2 - (self.cartesianCoordsPlatform[0] - self.cartesianCoordsBase[0])**2 - (self.cartesianCoordsPlatform[1] - self.cartesianCoordsBase[1])**2)
        self.home_pos = np.array([0, 0, z[0]])
        
        if verbose:
            print("---home_pos---")
            print(self.home_pos)
            print()

    # Standard rotation matrices
    def rotX(self, rot):
       return np.array([[1,     0,              0],
                        [0,     np.cos(rot),    -np.sin(rot)],
                        [0,     np.sin(rot),    np.cos(rot)]])

    def rotY(self, rot):
        return np.array([[np.cos(rot),  0,  np.sin(rot)],
                        [0,             1,  0],
                        [-np.sin(rot),  0,  np.cos(rot)]])

    def rotZ(self, rot):
        return np.array([[np.cos(rot),  -np.sin(rot), 0],
                        [np.sin(rot),   np.cos(rot),  0],
                        [0,             0,            1]])

    def calculate_leg_lengths(self, trans, rot):
        """Calculates inverse kinematics for leg lengths based on translation and rotation. USE THIS FOR LINEAR ACTUATORS.
        """
        trans = np.transpose(trans) 
        rot = np.transpose(rot)
        
        rotationMatrix = np.matmul(np.matmul(self.rotZ(rot[2]), self.rotY(rot[1])), self.rotX(rot[0]))

        # Find new leg positions based on translation and rotaion matrices
        legPositions = np.repeat(trans[:, np.newaxis], 6, axis=1) + np.repeat(self.home_pos[:, np.newaxis], 6, axis=1) + np.matmul(rotationMatrix, self.cartesianCoordsPlatform) - self.cartesianCoordsBase

        # Leg lengths are defined as the Euclidean L2 norm
        legLengths = np.linalg.norm(legPositions, axis=0)

        return legPositions, legLengths

    def calculate_servo_angles(self, trans, rot):
        """Calculates inverse kinematics for leg lengths based on translation and rotation. USE THIS FOR ROTATIONAL SERVO MOTORS.

        Uses calculated leg lengths and postisions to calculate required servo rotations
        """

        # calculate leg lengths and positions using IK
        legPositions, legLengths = self.calculate_leg_lengths(trans, rot)

        # Calculate servo angles for each leg
        ## Calculate e, f, and k (can't think of better naming) as per https://www.xarg.org/paper/inverse-kinematics-of-a-stewart-platform/
        e = 2 * self.servoHornLength * legPositions[2, :]
        g = legLengths**2 - (self.rodLength**2 - self.servoHornLength**2)

        servoAngles = []

        for i in range(6):
            f = 2 * self.servoHornLength * (np.cos(self.servoOffsetRotation[i]) * legPositions[0, i] + np.sin(self.servoOffsetRotation[i]) * legPositions[1, i])
            angle = np.arcsin(g[i] / np.sqrt(e[i]**2 + f**2)) - np.arctan2(f, e[i])
            if np.isnan(angle):
                raise ValueError("Wanted position cannot be achieved!")
            else:
                servoAngles.append(angle)

        return servoAngles
