#!/usr/bin/python

import time
import lib8relind
from relays import *

# set up linear actuator relays
relay1 = LinAct("", 1)
relay2 = LinAct("", 2)
relay3 = LinAct("", 3)
relay4 = LinAct("", 4)
relay5 = LinAct("", 5)
relay6 = LinAct("", 6)
relay7 = LinAct("", 7)
relay8 = LinAct("", 8)


def extend_all_relays():
    relay1.extend()
    relay2.extend()
    relay3.extend()
    relay4.extend()
    relay5.extend()
    relay6.extend()
    relay7.extend()
    relay8.extend()
    return True


def contract_all_relays():
    relay1.contract()
    relay2.contract()
    relay3.contract()
    relay4.contract()
    relay5.contract()
    relay6.contract()
    relay7.contract()
    relay8.contract()
    return True

# Contract then extend a single relay by number (1-8)
def contract_then_extend_relay(relay_num, contract_time=1, extend_time=1):
    relays = [relay1, relay2, relay3, relay4, relay5, relay6, relay7, relay8]
    if 1 <= relay_num <= 8:
        relay = relays[relay_num - 1]
        print("Contracting relay {}...".format(relay_num))
        relay.contract()
        time.sleep(contract_time)
        print("Extending relay {}...".format(relay_num))
        relay.extend()
        time.sleep(extend_time)
        return True
    else:
        print("Invalid relay number. Must be 1-8.")
        return False


def main():
    while True:
        print("\nRelay Test Menu:")
        print("1: Extend all relays")
        print("2: Contract all relays")
        print("3: Contract then extend a single relay")
        print("q: Quit")
        choice = str(input("Select test to run: "))()
        if choice == '1':
            extend_all_relays()
        elif choice == '2':
            contract_all_relays()
        elif choice == '3':
            try:
                relay_num = int(input("Enter relay number (1-8): "))
                contract_then_extend_relay(relay_num)
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 8.")
        elif choice == 'q':
            print("Exiting relay test.")
            break
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main()
