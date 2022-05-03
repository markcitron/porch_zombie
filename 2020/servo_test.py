#!/usr/bin/python3

import time, threading
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

kit.servo[0].angle = 170
time.sleep(1)
kit.servo[0].angle = 10
time.sleep(1)
kit.servo[0].angle = 170
time.sleep(1)
kit.servo[0].angle = 10
time.sleep(1)

kit.servo[2].angle = 180
time.sleep(1)
kit.servo[2].angle = 60
time.sleep(1)
kit.servo[2].angle = 135 
time.sleep(1)



