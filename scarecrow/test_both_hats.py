#!/usr/bin/python3

# load general utils
from threading import Thread
from time import sleep

# load library for the 8relay switch hat
import lib8relind
from relays import *

# load libraries for the robot hat control
from robot_hat import Servo, ADC
from robot_hat.utils import reset_mcu

# Setup the robot hat card
reset_mcu()
test_servo_number = 0 # using servo 0 for testing

# robohat servo test function(s)
def test_servo():
    print("Testing servo {}".format(test_servo_number))
    which_servo = test_servo_number
    servo_start = 90
    servo_end = -90
    Servo(int(which_servo)).angle(int(servo_start))
    sleep(1)
    Servo(int(which_servo)).angle(int(servo_end))
    sleep(1)
    Servo(int(which_servo)).angle(int(servo_start))

    return True

# Setup relays
relay1 = LinAct("", 1)
relay2 = LinAct("", 2)
relay3 = LinAct("", 3)
relay4 = LinAct("", 4)
relay5 = LinAct("", 5)
relay6 = LinAct("", 6)
relay7 = LinAct("", 7)
relay8 = LinAct("", 8)

# relay test functions
def test_all_relays():
    print("Extending all relays")
    relay1.extend()
    relay2.extend()
    relay3.extend()
    relay4.extend()
    relay5.extend()
    relay6.extend()
    relay7.extend()
    relay8.extend()

    sleep(1)

    print("Contracting all relays")
    relay1.contract()
    relay2.contract()
    relay3.contract()
    relay4.contract()
    relay5.contract()
    relay6.contract()
    relay7.contract()
    relay8.contract()

    return True


def main():
    print("Testing both hats...")

    servo_thread = Thread(target=test_servo)
    relay_thread = Thread(target=test_all_relays)

    servo_thread.start()
    relay_thread.start()

    servo_thread.join()
    relay_thread.join()

    print("done :-)")

if __name__ == "__main__":
    main()