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
        # Skull peek a boo
        #
        print("skull peak a boo")
        call_remote_addy(pz3, "extend_two/")
        sleep(3)
        call_remote_addy(pz3, "contract_two/")
        sleep(5)

        # wake the raven
        #
        print("wake the raven")
        call_remote_addy(pz0, "relay_3_trigger/")
        sleep(2)

        # open baby box
        #
        print("Open baby box.")
        call_remote_addy(pz2, "contract_one/")
        sleep(1)

        # hello plague doctor
        #
        print("Hello, plague doctor")
        relay_2.on()
        sleep(1)
        relay_2.off()
        sleep(10)

        ## close baby box
        #
        print("Closing baby box")
        call_remote_addy(pz2, "extend_one/")
        sleep(4)

        # hello pumpkin
        #
        print("Hello jack o lantern")
        relay_1.on()
        sleep(1)
        relay_2.off()
        sleep(1)

        # tilt alien - into view
        #
        print("tilt alien - hello")
        call_remote_addy(pz3, "extend_four/")
        sleep(1)

        # raise sad little skull
        #
        print("Hello sad little skull")
        call_remote_addy(pz3, "contract_eight/")
        sleep(3)
        call_remote_addy(pz3, "extend_eight/")
        sleep(3)

        # tilt alien - time to hide
        #
        print("tile alien - goodbye")
        call_remote_addy(pz3, "contract_four/")
        sleep(1)

        # open ghost cabinet
        #
        print("Opening ghost cabinet")
        call_remote_addy(pz2, "extend_two/")
        sleep(.5)
        call_remote_addy(pz2, "extend_three/")
        sleep(3)

        # wake the ghost
        #
        print("wake the ghost")
        call_remote_addy(pz0, "relay_1_trigger/")
        sleep(15)

        # close the ghost cabinet
        print("close the ghost cabinet")
        call_remote_addy(pz2, "contract_two/")
        sleep(.5)
        call_remote_addy(pz2, "contract_three/")
        sleep(3)

        # wake the ghost (rinse and repeat)
        #
        print("retrigger ghost")
        call_remote_addy(pz0, "relay_1_trigger/")
        sleep(1)

        # wake the raven
        #
        print("retrigger the raven")
        call_remote_addy(pz0, "relay_3_trigger/")
        sleep(2)

        # tilt alien - into view
        #
        print("tilt alien - hello again")
        call_remote_addy(pz3, "extend_four/")
        sleep(1)

        # raise sad little skull
        #
        print("sad little skull ...")
        call_remote_addy(pz3, "contract_eight/")
        sleep(3)
        call_remote_addy(pz3, "extend_eight/")
        sleep(3)

        # tilt alien - time to hide
        #
        print("tilt alien = goodbye again")
        call_remote_addy(pz3, "contract_four/")
        sleep(1)

        # Wait to reset
        #
        print("resetting ....")
        sleep(30)
        print("and ready for the next visitor")

    except Exception as e:
        print("ERROR: encountered error {0} while trying to process a new viitor".format(e))
        
    return True

def main():
    print("-------------------------------------------------")
    print("              Haunted Porch")
    print("                  pz_1_spst_relay")
    print("-------------------------------------------------")
    while True:
        motion.when_motion = someone_is_here
        sleep(.1)
    return True

if __name__ == "__main__":
    main()
