import sys, tty, termios
from DynamixelControl import DynamixelControl

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
def getch():
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

index = 0
DXL_MINIMUM_POSITION_VALUE  = 204
DXL_MAXIMUM_POSITION_VALUE  = 820
dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]

ids = [2, 3, 4, 5, 6, 7]

dc = DynamixelControl(DXL_ids = ids, verbose=True)

degrees = [{"id" : i, "degrees" : 90} for i in ids]

dc.move_degrees(degrees)
while 1:
    moving = dc.get_moving_status()
    if not all(moving):
        break

"""
while 1:
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        del dc
        break

    goal_positions = []

    for i in ids:
        gp = dxl_goal_position[index]

        if i % 2 != 0:
            gp = 1024 - gp

        goal_positions.append({"id": i, "position" : gp})

    try:
        dc.sync_write(goal_positions)
    except ValueError as ve:
        print(ve)
        del dc
        break
    except Exception as e:
        print(e)
        del dc
        break

    # Wait until servos have stopped moving
    while 1:
        moving = dc.get_moving_status()
        if not all(moving):
            break

    # Change goal position
    if index == 0:
        index = 1
    else:
        index = 0
"""
