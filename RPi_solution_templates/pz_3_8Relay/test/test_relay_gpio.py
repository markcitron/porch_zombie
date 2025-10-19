#!/usr/bin/python3

from gpiozero import MotionSensor
from signal import pause
import time
import lib8relind

# globals
pir = MotionSensor(16) # bind motion sensor to GPIO pin 16
def someone_is_here():
    print("Motion triggered.") 
    lib8relind.set_all(0, 255)
    time.sleep(5)
    lib8relind.set_all(0, 0)
    time.sleep(5)
    return True

def main():
    while True:
        pir.when_motion = someone_is_here()
        time.sleep(1)
    return True

if __name__ == "__main__":
    main()
