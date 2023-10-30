#!/usr/bin/python3

from gpiozero import MotionSensor
from signal import pause
import time, requests

# globals
working = False
relay2_addr = "http://10.10.0.83:5000/"
pir = MotionSensor(18) # bind motion sensor to GPIO pin 18

def someone_is_here():
    print("------------------------------- Someone is here ------------------------------")
    try: 
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
    except Exception as e:
        print("Error encountered calling {0}, encountered exception: {1}".format(relay2_addr, e))
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

