import KeyPoller

with KeyPoller.KeyPoller() as keyPoller:
    while True:
        c = keyPoller.poll()
        if not c is None:
            if c == "c":
                break
            if c == "w":
                print("north")
            if c == "a":
                print("west")
            if c == "s":
                print("south")
            if c == "d":
                print("east")
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

