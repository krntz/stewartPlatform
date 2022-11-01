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
    print(trans, rot)
    return trans, rot

s = StewartPlatform(100.089, 50, 26.5, 120, 0.229, 0.229, np.radians(60), verbose=False)

servo_ids = [2, 3, 4, 5, 6, 7]
dc = DynamixelControl(servo_ids)

trans = np.array([0, 0, 0])
rot = np.array([0, 0, 0])

# move servos to home position
update_servos(trans, rot)

move_speed = 10

with KeyPoller.KeyPoller() as keyPoller:
    while True:
        old_trans = trans
        old_rot = rot
        c = keyPoller.poll()
        try:
            if not c is None:
                if c == "c":
                    break
                if c == "w":
                    new_trans = old_trans + np.array([move_speed, 0, 0])
                    trans, rot = update_servos(new_trans, old_rot)
                if c == "a":
                    new_trans = old_trans - np.array([0, move_speed, 0])
                    trans, rot = update_servos(new_trans, old_rot)
                if c == "s":
                    new_trans = old_trans - np.array([move_speed, 0, 0])
                    trans, rot = update_servos(new_trans, old_rot)
                if c == "d":
                    new_trans = old_trans + np.array([0, move_speed, 0])
                    trans, rot = update_servos(new_trans, old_rot)
                if c == "q":
                    new_rot = old_rot - np.array([0, 0, move_speed])
                    trans, rot = update_servos(old_trans, new_rot)
                if c == "e":
                    new_rot = old_rot + np.array([0, 0, move_speed])
                    trans, rot = update_servos(old_trans, new_rot)
                if c == "r":
                    new_trans = old_trans + np.array([0, 0, move_speed])
                    trans, rot = update_servos(new_trans, old_rot)
                if c == "f":
                    new_trans = old_trans - np.array([0, 0, move_speed])
                    trans, rot = update_servos(new_trans, old_rot)
                if c == "i":
                    new_rot = old_rot - np.array([move_speed, 0, 0])
                    trans, rot = update_servos(old_trans, new_rot)
                if c == "k":
                    new_rot = old_rot + np.array([move_speed, 0, 0])
                    trans, rot = update_servos(old_trans, new_rot)
                if c == "j":
                    new_rot = old_rot - np.array([0, move_speed, 0])
                    trans, rot = update_servos(old_trans, new_rot)
                if c == "l":
                    new_rot = old_rot + np.array([0, move_speed, 0])
                    trans, rot = update_servos(old_trans, new_rot)
        except ValueError as ve:
           print(ve)
           trans = old_trans
           rot = old_rot
