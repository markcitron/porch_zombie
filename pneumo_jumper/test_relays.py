#!/usr/bin/python

import time
from relays import *

# Set up relays 
relay1 = LinAct("Relay 1", 26)  # BCM pin 26
relay2 = LinAct("Relay 2", 20)  # BCM pin 20
relay3 = LinAct("Pneumo Jumper", 21)  # BCM pin 21

def main():
    try:
        while True:
            print("Activating Relay 1")
            relay1.contract()
            time.sleep(1)
            relay1.extend()
            time.sleep(1)

            print("Activating Relay 2")
            relay2.contract()
            time.sleep(1)
            relay2.extend()
            time.sleep(1)

            print("Activating Pneumo Jumper")
            relay3.contract()
            time.sleep(1)
            relay3.extend()
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        gpio_cleanup()
