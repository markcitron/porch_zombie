#!/usr/bin/python3

import time
from relays import *

# Set up relays as in mqtt_cs_and_ec.py
relay2 = LinAct("Coffin Skeleton", 20)

def main():
    try:
        print("Raising Coffin Skeleton")
        relay2.extend()
        time.sleep(.1)
    except Exception as e:
        print("unable to raise skeleton: {}".format(e))


if __name__ == "__main__":
    main()