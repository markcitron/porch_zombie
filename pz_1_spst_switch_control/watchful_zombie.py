#!/usr/bin/python3

import requests
from gpiozero import MotionSensor
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

# set globals
pz1 = "http://10.10.0.253:5000/"
pz2 = "http://10.10.0.188:5000/"
pz3 = "http://10.10.0.83:5000/"

# set componant locations
motion = MotionSensor(17)

def call_remote_addy(base_addy, action):
    try:
        a = requests.get(base_addy+action)
        print("calling: {0}{1}".format(base_addy, action))
    except Exception as e:
        print("Error: failed call to: {0}".format(base_addy+action))
        print("Exception: {0}".format(e))
    return True

def someone_is_here():
    print("------------------------------- Someone is here ------------------------------")
    try: 
        print("Welcome to our house!!!")

        # open/close the Baby Box
        call_remote_addy(pz2, "contract_one/")
        sleep(10)
        call_remote_addy(pz2, "extend_one/")
        sleep(20)

    except Exception as e:
        print("ERROR: encountered error {0} while trying to process a new viitor".format(e))
        
    return True

def main():
    print("-------------------------------------------------")
    print("              Haunted Porch")
    print("-------------------------------------------------")
    while True:
        motion.when_motion = someone_is_here
        sleep(.1)
    return True

if __name__ == "__main__":
    main()
