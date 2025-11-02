#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

<<<<<<< HEAD
=======
GPIO.cleanup()
>>>>>>> 8c31b29eda0ad6cdcab8273d6ed029af0993864a
GPIO.setmode(GPIO.BCM)

class LinAct():
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

