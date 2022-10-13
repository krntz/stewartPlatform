import KeyPoller

# all measurements in mm and degrees
d = 20 # Length of rod
h = 25.5 # Distance between servo shaft and servo horn anchor
alpha_k = 0 # Angle of h

base_radius = 75
base_anchors = []

platform_radius = 
platform_anchors = []

with KeyPoller.KeyPoller() as keyPoller:
    while True:
        c = keyPoller.poll()
        if not c is None:
            if c == "c":
                break
            if c == "w":
                print("translate north")
            if c == "a":
                print("translate west")
            if c == "s":
                print("translate south")
            if c == "d":
                print("translate east")
            if c == "q":
                print("yaw west")
            if c == "e":
                print("yaw east")
            if c == "r":
                print("rise")
            if c == "f":
                print("fall")
            if c == "i":
                print("pitch down")
            if c == "k":
                print("pitch up")
            if c == "j":
                print("roll west")
            if c == "l":
                print("roll east")

