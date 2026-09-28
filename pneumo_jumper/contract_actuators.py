#!/usr/bin/python3

import time
from relays import *

# Set up relays as in mqtt_cs_and_ec.py
relay2 = LinAct("Coffin Skeleton", 20)
relay3 = LinAct("Coffin Skeleton 2", 21)


def main():
    try:
        print("Contracting actuators") 
        relay2.contract()
        time.sleep(.1)
        relay3.contract()
        time.sleep(.1)
    except Exception as e:
        print("unable to extend actuators: {}".format(e))


if __name__ == "__main__":
    main()
