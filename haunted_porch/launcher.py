#!/usr/bin/python3

from gpiozero import MotionSensor
from signal import pause
import time, requests

# globals
working = False
pz1_addr = "http://10.10.0.253:5000/"
pz2_addr = "http://10.10.0.83:5000/"
pz3_addr = "http://10.10.0.188:5000/"
pir = MotionSensor(18) # bind motion sensor to GPIO pin 18

def call_remote_addy(base_addy, action):
    try:
        a = requests.get(base_addy+"_addr"+action)
    except Exception as e:
        print("Error: failed call to: {0}".format(base_addy+action))
        print("Exception: {0}".format(e))
    return True


def someone_is_here():
    print("------------------------------- Someone is here ------------------------------")
    try: 
        # for demo testing
        """
        print("Alien tilt out ...") 
        a = requests.get(relay2_addr+'extend_three/') 
        time.sleep(5) 
        print("Baby box opening ...") 
        x = requests.get(relay2_addr+'extend_two/') 
        time.sleep(5)
        print("Alien tilt back...") 
        b = requests.get(relay2_addr+'contract_three/') 
        time.sleep(5) 
        print("Baby box closing ...") 
        y = requests.get(relay2_addr+'contract_two/') 
        time.sleep(5)
        """

        # Plague doctor
        call_remote_addy(pz1, "contract_two/")
        tile.sleep(1)
        call_remote_addy(pz1, "extend_two/")
        time.sleep(5)

        # Tilting Freddy
        # .. tilt down
        call_remote_addy(pz1, "extend_three/")
        time.sleep(5)
        # .. tilt back up
        call_remote_addy(pz1, "contract_three/")
        time.sleep(1)

        # Crow
        call_remote_addy(pz3, "extend_seven/")
        time.sleep(1)
        call_remote_addy(pz3, "contract_seven/")

        # Baby box
        # .. open
        time.sleep(10)
        call_remote_addy(pz2, "extend_one/")
        time.sleep(1)
        # .. close
        time.sleep(10)
        call_remote_addy(pz2, "contract_one/")

        # Electric box
        time.sleep(1)
        call_remote_addy(pz3, "contract_six/")
        time.sleep(1)
        call_remote_addy(pz3, "extend_six/")
        time.sleep(1)

        # Ghost box open
        # .. open left door
        call_remote_addy(pz2, "extend_two/")
        time.sleep(1)
        # .. open right door
        call_remote_addy(pz2, "extened_three/")
        time.sleep(15)

        # Boxed ghost
        call_remote_addy(pz3, "extend_/")
        time.sleep(1)
        call_remote_addy(pz3, "contract_/")
        time.sleep(20)

        # Evil Cherub
        call_remote_addy(pz3, "extend_five/")
        time.sleep(1)
        call_remote_addy(pz3, "contract_five/")
        time.sleep(1)

        # Ghost box close
        # .. close left door
        call_remote_addy(pz2, "contract_two/")
        time.sleep(1)
        # .. close right door
        call_remote_addy(pz2, "contract_three/")
        time.sleep(10)

        # Jack-o-lantern
        call_remote_addy(pz3, "contract_one/")
        time.sleep(1)
        call_remote_addy(pz3, "extend_one/")
        time.sleep(1)

        # final pause
        time.sleep(20)

        # all done.

    except Exception as e:
        print("ERROR: encountered error {0} while trying to process a new viitor".format(e))
    return True

def main():
    # Intro
    print("-------------------------------------------------")
    print("              Haunted Porch")
    print("-------------------------------------------------")

    # start things up 

    while True:
        pir.when_motion = someone_is_here
        time.sleep(1)

    # if no motion
    # pir.when_no_motion = no_motion_function

if __name__ == "__main__":
    main()

