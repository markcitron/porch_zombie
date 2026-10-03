#!/usr/bin/python3

import time
from relays import *

relay1 = LinAct("Zombie Closet", 26)

def main():
    try:
        print("Closing Zombie Closet")
        relay1.extend()
        time.sleep(.1)
    except Exception as e:
        print("unable to close: {}".format(e))


if __name__ == "__main__":
    main()