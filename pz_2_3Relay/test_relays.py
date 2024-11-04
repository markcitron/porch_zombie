#!/usr/bin/python3

from relays import *
from time import sleep

# set up relays
relay1 = LinAct("one", 26)
relay2 = LinAct("two", 20)
relay3 = LinAct("three", 21)

def main():
    test_cycles = 1
    delay = 1
    while test_cycles < 4:
        relay1.extend()
        sleep(delay)
        relay2.extend()
        sleep(delay)
        relay3.extend()
        sleep(delay)

        relay1.contract()
        sleep(delay)
        relay2.contract()
        sleep(delay)
        relay3.contract()
        sleep(delay)

        test_cycles = test_cycles + 1

    gpio_cleanup()

    return True

if __name__ == "__main__":
    main()
