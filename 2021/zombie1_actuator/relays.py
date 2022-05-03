#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

class LinArct():
    def __init__ (self, name, pin_id):
        self.name = name
        self.pin_id = pin_id
        GPIO.setup(pin_id, GPIO.OUT)

    def contract(self):
        GPIO.output(self.pin_id, GPIO.HIGH)

    def extend(self):
        GPIO.output(self.pin_id, GPIO.LOW)

        
def gpio_cleanup():
    GPIO.cleanup()
    return True

