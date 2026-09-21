#!/usr/bin/python3

import time
from relays import *

# Set up relays as in mqtt_cs_and_ec.py
relay2 = LinAct("Coffin Skeleton", 20)
relay3 = LinAct("Coffin Skeleton 2", 21)

def main():
    try:
        print("extending actuators")
        relay2.extend()
        relay3.extend()
    except Exception as e:
        print("unable to extend actuators: {}".format(e))


if __name__ == "__main__":
    main()
