#!/usr/bin/python3

from gpiozero import LED, MotionSensor
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

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

def someone_is_here():
    print("Welcome to our house!!!")

    delay = .1

    relay_1.on()
    sleep(delay)
    relay_2.on()
    sleep(delay)
    relay_3.on()
    sleep(delay)
    relay_4.on()
    sleep(delay)
    relay_5.on()
    sleep(delay)
    relay_6.on()
    sleep(delay)
    relay_7.on()
    sleep(delay)
    relay_8.on()
    sleep(delay)

    relay_1.off()
    sleep(delay)
    relay_2.off()
    sleep(delay)
    relay_3.off()
    sleep(delay)
    relay_4.off()
    sleep(delay)
    relay_5.off()
    sleep(delay)
    relay_6.off()
    sleep(delay)
    relay_7.off()
    sleep(delay)
    relay_8.off()
    sleep(delay)

    sleep(5)

    return True

def main():
    print("started up and waiting ...")
    while True:
        motion.when_motion = someone_is_here
    return True

if __name__ == "__main__":
    main()
