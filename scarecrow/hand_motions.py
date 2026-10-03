#!/usr/bin/python3
from robot_hat import Servo
from robot_hat.utils import reset_mcu
from time import sleep

reset_mcu()
sleep(1)

""" Fingers:
        right_thumb -> 3
        right_index -> 0
        right_middle -> 2
        right_ring -> 1
        right_pinkie -> 4
        left_thumb -> 10
        left_index -> 8
        left_middle -> 7
        left_ring -> 9
        left_pinkie -> 6

    Motion: 
        for fingers on left hand: -90 closed, 90 pointing
        for fingers on right hand: 90 closed, -90 pointing

        """
def open_hand(which_hand) -> bool:
    if which_hand == "left": 
        print("opening left hand") 
        servo_moveto = -90 
        Servo(6).angle(int(servo_moveto)) 
        Servo(7).angle(int(servo_moveto))
        Servo(8).angle(int(servo_moveto))
        Servo(9).angle(int(servo_moveto))
        Servo(10).angle(int(90))
        return True
    elif which_hand == "right":
        servo_moveto = 90
        print("opening right hand")
        Servo(0).angle(int(servo_moveto))
        Servo(1).angle(int(servo_moveto))
        Servo(2).angle(int(servo_moveto))
        Servo(4).angle(int(servo_moveto))
        Servo(3).angle(int(-90))
        return True
    else:
        print("No hand designated")
        return True

def close_hand(which_hand) -> bool:
    if which_hand == "left": 
        print("closing left hand") 
        servo_moveto = 90 
        Servo(6).angle(int(servo_moveto)) 
        Servo(7).angle(int(servo_moveto))
        Servo(8).angle(int(servo_moveto))
        Servo(9).angle(int(servo_moveto))
        Servo(10).angle(int(-90))
        return True
    elif which_hand == "right":
        servo_moveto = -90
        print("closing right hand")
        Servo(0).angle(int(servo_moveto))
        Servo(1).angle(int(servo_moveto))
        Servo(2).angle(int(servo_moveto))
        Servo(4).angle(int(servo_moveto))
        Servo(3).angle(int(90))
        return True
    else:
        print("No hand designated")
        return True

def test_hand_motions():
    while True: 
        print("Haunted Porch - Scarecrow") 
        print("-------------------------") 
        print("Testing hands") 
        print("|") 
        print("| 1. open left hand") 
        print("| 2. close left hand") 
        print("| 3. open right hand") 
        print("| 4. close right hand") 
        print("|") 
        what_to_do = input("|-> ? ")
        if what_to_do == "1": 
            open_hand("left") 
        elif what_to_do == "2": 
            close_hand("left") 
        elif what_to_do == "3": 
            open_hand("right") 
        elif what_to_do == "4": 
            close_hand("right") 
        elif what_to_do == "q": 
            print("Thanks for playing :-)") 
            break


if __name__ == '__main__':
    test_hand_motions()
