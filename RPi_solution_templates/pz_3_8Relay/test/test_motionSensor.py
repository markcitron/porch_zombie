#!/usr/bin/python3

from gpiozero import MotionSensor
import time
import lib8relind

# globals
pir = MotionSensor(4) # bind motion sensor to GPIO pin 16

def someone_is_here():
    print("Someone is here...")
    time.sleep(1)
    return True

def main():
    while True:
        pir.when_motion = someone_is_here
        time.sleep(1)

if __name__ == "__main__":
    main()
