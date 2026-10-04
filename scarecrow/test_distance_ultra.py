#!/usr/bin/python

from robot_hat import Ultrasonic, Pin
import time

ultrasonic = Ultrasonic(trig=Pin("D2"), echo=Pin("D3"))

while True:
    distance = ultrasonic.read()
    print("Distance: {distance} cm", end="", flush=True)
    time.sleep(0.2)
