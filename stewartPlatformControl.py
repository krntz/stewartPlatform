import KeyPoller
import numpy as np
import time
from StewartPlatform import StewartPlatform
from DynamixelControl import DynamixelControl

s = StewartPlatform(75, 75, 25.5, 85, 0.229, 0.229, np.radians(60))

servo_ids = [2, 3, 4, 5, 6, 7]
dc = DynamixelControl(servo_ids)

trans = np.array([0, 0, 0])
rot = np.array([0, 0, 0])

with KeyPoller.KeyPoller() as keyPoller:
    while True:
        new_trans = trans
        new_rot = rot
        c = keyPoller.poll()
        if not c is None:
            if c == "c":
                break
            if c == "w":
                new_trans += np.array([1, 0, 0])
            if c == "a":
                new_trans -= np.array([0, 1, 0])
            if c == "s":
                new_trans -= np.array([1, 0, 0])
            if c == "d":
                new_trans += np.array([0, 1, 0])
            if c == "q":
                new_rot -= np.array([0, 0, 1])
            if c == "e":
                new_rot += np.array([0, 0, 1])
            if c == "r":
                new_trans += np.array([0, 0, 1])
            if c == "f":
                new_trans -= np.array([0, 0, 1])
            if c == "i":
                new_rot -= np.array([1, 0, 0])
            if c == "k":
                new_rot += np.array([1, 0, 0])
            if c == "j":
                new_rot -= np.array([0, 1, 0])
            if c == "l":
                new_rot += np.array([0, 1, 0])

        try:
            servo_angles = np.rad2deg(s.calculate_servo_angles(new_trans, np.deg2rad(new_rot)))
            goal_positions = [{"id" : servo_ids[i], "degrees" : j} for i, j in enumerate(servo_angles)]
            dc.move_degrees(goal_positions)
        except ValueError as ve:
            print(ve)
        else:
            trans = new_trans
            rot = new_rot

        print(trans, rot)
