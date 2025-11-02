#!/usr/bin/python3

import time
from relays import *

# Set up relays as in mqtt_cs_and_ec.py
relay1 = LinAct("Coffin Skeleton", 26)
relay2 = LinAct("Electro Closet", 20)
relay3 = LinAct("Electro Closet", 21)

def main():
    try:
        print("extending actuators")
        relay1.extend()
        relay2.extend()
        relay3.extend()
    except Exception as e:
        print("unable to extend actuators: {}".format(e))


if __name__ == "__main__":
    main()
