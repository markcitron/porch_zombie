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
            time.sleep(0.03)

        self.current_val = new_val

    def get_pos(self):
        return self.current_val

# initialize servos
# Head
s14 = Motor(14, kit, 50)
s15 = Motor(15, kit, 110)

# arm
s0 = Motor(0, kit, 10) # arm 
s2 = Motor(2, kit, 135) # Shoulder  

def test_upper_arm():
    s0.move_to(170)
    s0.move_to(10)

def test_shoulder():
    s2.move_to(45)
    s2.move_to(175)
    s2.move_to(135)

def test_arm():
    # set threads
    t1 = threading.Thread(target=test_upper_arm)
    t2 = threading.Thread(target=test_shoulder)
    
    # start threads
    t1.start()
    t2.start()

    # join threads
    t1.join()
    t2.join()

if __name__ == "__main__":
    main()
