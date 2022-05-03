#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

def main():
    print("Relay test")
    print("  ... pinned to 26 for switch 1") 
    
    GPIO.setmode(GPIO.BCM)
    # GPIO.setmode(GPIO.BOARD)
    LIN_ACT = 26
    GPIO.setup(LIN_ACT, GPIO.OUT)
    GPIO.output(LIN_ACT, GPIO.HIGH)
    time.sleep(5)
    GPIO.output(LIN_ACT, GPIO.LOW)
    GPIO.cleanup()

    print("All done")



if __name__ == "__main__":
    main()
