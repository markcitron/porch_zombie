#!/usr/bin/python3

from gpiozero import MotionSensor
from signal import pause
import time

pir = MotionSensor(18)

def motion_function():
    print("-------------------------------Motion detected------------------------------")
    time.sleep(1)
    return True

def no_motion_function():
    print("Motion stopped")
    return True

def main():
    pir.when_motion = motion_function
    # pir.when_no_motion = no_motion_function

    pause()

if __name__ == "__main__":
    main()
