#!/usr/bin/python3

import time, threading
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

class Motor():
    def __init__(self, s_id, kit, i_val):
        # set values
        self.current_val = i_val
        self.s_id = s_id

        # move to initial value
        kit.servo[s_id].angle = i_val

    def move_to(self, new_val):
        inc = 1
        if self.current_val > new_val:
            inc = -1
        pos = self.current_val
        while True:
            kit.servo[self.s_id].angle = pos
            pos += inc
            if inc > 0 and pos >= new_val:
                break
            elif inc < 0 and pos <= new_val:
                break
            time.sleep(0.01)

        self.current_val = new_val

    def get_pos(self):
        return self.current_val

def main():
    # setup
    # Head
    # s14 = Motor(14, kit, 50)
    # s15 = Motor(15, kit, 110)
    # arm
    # s0 = Motor(0, kit, 90) # Shoulder  
    s1 = Motor(1, kit, 0) # arm
    kit.servo[1].angle = 60
    time.sleep(1)
    kit.servo[1].angle = 0

    # test
    # s14.move_to(10)
    # s14.move_to(140)
    # s14.move_to(50)

    # s15.move_to(30)
    # s15.move_to(180)
    # s15.move_to(110)

    s1.move_to(0)
    s1.move_to(180)
    s1.move_to(0)

    # s0.move_to(10)
    # s0.move_to(170)
    # s0.move_to(90)


if __name__ == "__main__":
    main()