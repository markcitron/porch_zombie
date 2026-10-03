#!/usr/bin/python3

import time
from relays import *

# Set up relays as in mqtt_cs_and_ec.py
relay1 = LinAct("Zombie Closet", 26)

def main():
    try:
        print("Opening Zombie Closet")
        relay1.extend()
        time.sleep(.1)
    except Exception as e:
        print("unable to trigger open: {}".format(e))


if __name__ == "__main__":
    main()