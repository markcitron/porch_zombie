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
s14 = Motor(14, kit, 115)
s15 = Motor(15, kit, 0) # 40 is straight forward

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

def head_side_to_side():
    s14.move_to(20)
    s14.move_to(180)
    s14.move_to(115)

def head_up_and_down():
    s15.move_to(0)
    s15.move_to(90)
    s15.move_to(0)

def lrap():
    """ Look right and point """
    t1 = threading.Thread(target=s15.move_to, args=(60,)) 
    t2 = threading.Thread(target=s14.move_to, args=(35,))
    t3 = threading.Thread(target=s0.move_to, args=(70,))
    t4 = threading.Thread(target=s2.move_to, args=(100,))

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()

def blrap():
    """ Back from look right and point """
    t1 = threading.Thread(target=s15.move_to, args=(0,))  
    t2 = threading.Thread(target=s14.move_to, args=(115,))
    t3 = threading.Thread(target=s0.move_to, args=(10,))
    t4 = threading.Thread(target=s2.move_to, args=(135,))

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()

def no_dont_think_so():
    """ moving head up, look right and then side to side 
         |---------------------------------|
         |  Servo |   Which   |  position  |
         |---------------------------------|
         |   s15  |    up     |     60     |
         |   s15  |   down*   |     0      |
         |   s14  |  rt side  |     35     |
         |   s14  |  lt side* |     115    |
         |---------------------------------|
                           * Final position """ 
    # head up and right
    t1 = threading.Thread(target=s15.move_to, args=(60,)) 
    t2 = threading.Thread(target=s14.move_to, args=(35,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    time.sleep(1)

    # no, no
    s14.move_to(115) # right -> left
    s14.move_to(35) # left -> right
    s14.move_to(115) # right -> left
    s14.move_to(35) # left -> right

    # and back again
    t3 = threading.Thread(target=s15.move_to, args=(0,)) 
    t4 = threading.Thread(target=s14.move_to, args=(115,))
    t3.start()
    t4.start()
    t3.join()
    t4.join()


def test_head():
    # Set threads
    t1 = threading.Thread(target=head_side_to_side)
    t2 = threading.Thread(target=head_up_and_down)
    # start threads
    t1.start()
    t2.start()
    # joing threads
    t1.join()
    t2.join()

def go_go_zombie():
    pass
