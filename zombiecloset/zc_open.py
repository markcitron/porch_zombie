#!/usr/bin/python3

import time
from relays import *

relay1 = LinAct("Zombie Closet", 26)

def main():
    try:
        print("Opening Zombie Closet")
        relay1.contract()
        time.sleep(.1)
    except Exception as e:
        print("unable to trigger open: {}".format(e))


if __name__ == "__main__":
    main()