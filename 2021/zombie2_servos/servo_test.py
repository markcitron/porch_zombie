#!/usr/bin/python3

import time
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

kit.servo[0].angle = 130
time.sleep(1)
kit.servo[0].angle = 10
time.sleep(1)
kit.servo[0].angle = 130
time.sleep(1)
kit.servo[0].angle = 10
time.sleep(1)