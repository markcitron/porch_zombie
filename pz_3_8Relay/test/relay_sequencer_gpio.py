#!/usr/bin/python3

from gpiozero import MotionSensor
from signal import pause
import time
import lib8relind

# globals
def toggle(pin, on_off):
    return True

def main():
    # reset
    delay = .1
    lib8relind.set_all(0, 0)

    for i in range(8):
        current_relay = i + 1
        lib8relind.set(0, current_relay, 1)
        time.sleep(delay)
    
    # reset 
    lib8relind.set_all(0, 0)

    cont_looping = 1
    while cont_looping < 3:
        time.sleep(delay)
        lib8relind.set(0,1,1)
        time.sleep(delay)
        lib8relind.set(0,3,1)
        time.sleep(delay)
        lib8relind.set(0,7,1)
        time.sleep(delay)
        lib8relind.set(0,5,1)
        time.sleep(delay)
        lib8relind.set(0,6,1)
        time.sleep(delay)
        lib8relind.set(0,8,1)
        time.sleep(delay)
        lib8relind.set(0,4,1)
        time.sleep(delay)
        lib8relind.set(0,2,1)
        time.sleep(delay)


        lib8relind.set(0,2,0)
        time.sleep(delay)
        lib8relind.set(0,4,0)
        time.sleep(delay)
        lib8relind.set(0,8,0)
        time.sleep(delay)
        lib8relind.set(0,6,0)
        time.sleep(delay)
        lib8relind.set(0,5,0)
        time.sleep(delay)
        lib8relind.set(0,7,0)
        time.sleep(delay)
        lib8relind.set(0,3,0)
        time.sleep(delay)
        lib8relind.set(0,1,0)
        time.sleep(delay)

        cont_looping = cont_looping + 1
    
    cont_looping = 1
    while cont_looping < 3:
        lib8relind.set(0,1,1)
        time.sleep(delay)
        lib8relind.set(0,3,1)
        time.sleep(delay)
        lib8relind.set(0,7,1)
        time.sleep(delay)
        lib8relind.set(0,5,1)
        time.sleep(delay)
        lib8relind.set(0,6,1)
        time.sleep(delay)
        lib8relind.set(0,8,1)
        time.sleep(delay)
        lib8relind.set(0,4,1)
        time.sleep(delay)
        lib8relind.set(0,2,1)
        time.sleep(delay)

        lib8relind.set(0,1,0)
        time.sleep(delay)
        lib8relind.set(0,3,0)
        time.sleep(delay)
        lib8relind.set(0,7,0)
        time.sleep(delay)
        lib8relind.set(0,5,0)
        time.sleep(delay)
        lib8relind.set(0,6,0)
        time.sleep(delay)
        lib8relind.set(0,8,0)
        time.sleep(delay)
        lib8relind.set(0,4,0)
        time.sleep(delay)
        lib8relind.set(0,2,0)
        time.sleep(delay)

        cont_looping = cont_looping + 1

    return True

if __name__ == "__main__":
    main()
