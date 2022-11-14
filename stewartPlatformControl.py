import KeyPoller
import numpy as np
import time
from StewartPlatform import StewartPlatform
from DynamixelControl import DynamixelControl
import time

def update_servos(new_trans, new_rot):
    try:
        servo_angles = np.rad2deg(s.calculate_servo_angles(new_trans, np.deg2rad(new_rot)))
        goal_positions = [{"id" : servo_ids[i], "degrees" : j} for i, j in enumerate(servo_angles)]
        dc.move_degrees(goal_positions)
    except ValueError as ve:
        # give the exception to the main loop
        raise
    else:
        trans = new_trans
        rot = new_rot
    return trans, rot

s = StewartPlatform(radiusBase = 100.089, 
                    radiusPlatform = 50, 
                    servoHornLength = 26.5, 
                    rodLength = 120, 
                    anchorAngleBase = 0.229, 
                    anchorAnglePlatform = 0.229, 
                    platform_rot = np.radians(60), 
                    verbose=False)

dc = DynamixelControl([2, 3, 4, 5, 6, 7])

trans = np.array([0, 0, 0])
rot = np.array([0, 0, 0])

# move servos to home position
update_servos(trans, rot)

move_speed = 20

# TODO:
# - Make this a more robust input handler, maybe something from a game engine?

with KeyPoller.KeyPoller() as keyPoller:
    while True:
        c = keyPoller.poll()
        if not c is None:
                if c == "c":
                    break
                if c == "w":
                    trans += np.array([move_speed, 0, 0])
                if c == "a":
                    trans -= np.array([0, move_speed, 0])
                if c == "s":
                    trans -= np.array([move_speed, 0, 0])
                if c == "d":
                    trans += np.array([0, move_speed, 0])
                if c == "q":
                    rot -= np.array([0, 0, move_speed])
                if c == "e":
                    rot += np.array([0, 0, move_speed])
                if c == "r":
                    trans += np.array([0, 0, move_speed])
                if c == "f":
                    trans -= np.array([0, 0, move_speed])
                if c == "i":
                    rot -= np.array([move_speed, 0, 0])
                if c == "k":
                    rot += np.array([move_speed, 0, 0])
                if c == "j":
                    rot -= np.array([0, move_speed, 0])
                if c == "l":
                    rot += np.array([0, move_speed, 0])
                if c == " ":
                    trans = np.array([0, 0, 0])
                    rot = np.array([0, 0, 0])
        try:
            update_servos(trans, rot)
        except ValueError as ve:
           print(ve)

