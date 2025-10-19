#!/usr/bin/python3

import requests
from gpiozero import MotionSensor, LED
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

# set globals
pz0 = "http://10.10.0.14:5000/"
pz1 = "http://10.10.0.253:5000/"
pz2 = "http://10.10.0.188:5000/"
pz3 = "http://10.10.0.83:5000/"

# set componant locations
relay_1 = LED(5)
relay_2 = LED(6)
relay_3 = LED(13)
relay_4 = LED(16)
relay_5 = LED(19)
relay_6 = LED(20)
relay_7 = LED(21)
relay_8 = LED(26)
motion = MotionSensor(17)

def call_remote_addy(base_addy, action):
    # function call_remote_addy
    # params:
    #    base_addy: base address to call, explicitely set in the globals section above
    #    action: external function to all, these will be called from the remote flask app.
    #
    # TODO: should have the remote addresses in a configuration file instead so that they only
    #       have to be changed in one place.
    #
    try:
        a = requests.get(base_addy+action)
        print("calling: {0}{1}".format(base_addy, action))
    except Exception as e:
        print("Error: failed call to: {0}".format(base_addy+action))
        print("Exception: {0}".format(e))
    return True

def someone_is_here():
    # function: someone_is_here
    # params: none
    #
    # Description:
    #    function to be called when someone triggers the motion sensor.  All of the motion
    #    is in a single call and nothing further is done until this function returns.  
    #
    print("------------------------------- Someone is here ------------------------------")
    try: 
        print("Welcome to our house!!!")
        # Open/close the Baby Box
        #
        call_remote_addy(pz2, "contract_one/")
        sleep(10)
        call_remote_addy(pz2, "extend_one/")
        sleep(20)

        # to call any of the local switches, use the following format:
        #     relay_#.[on|off]() to turn then on or off respectively.
        #

    except Exception as e:
        print("ERROR: encountered error {0} while trying to process a new viitor".format(e))
        
    return True

def main():
    print("-------------------------------------------------")
    print("              Haunted Porch")
    print("                  pz_0_spst_relay")
    print("-------------------------------------------------")
    while True:
        motion.when_motion = someone_is_here
        sleep(.1)
    return True

if __name__ == "__main__":
    main()
