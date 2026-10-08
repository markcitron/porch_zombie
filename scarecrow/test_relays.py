#!/usr/bin/python3

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
relays = [relay1, relay2, relay3, relay4, relay5, relay6, relay7, relay8]


def read_relay_state(relay_num):
    state = lib8relind.get(0, relay_num)
    state_name = "contract (1)" if state == 1 else "extend (0)"
    print("Controller readback for relay {}: {}".format(relay_num, state_name))
    return state


def read_all_relay_states():
    states = [lib8relind.get(0, relay_num) for relay_num in range(1, 9)]
    print(
        "Controller readback: "
        + ", ".join(
            "{}={}".format(relay_num, state)
            for relay_num, state in enumerate(states, start=1)
        )
    )
    return states


def extend_all_relays():
    relay1.extend()
    relay2.extend()
    relay3.extend()
    relay4.extend()
    relay5.extend()
    relay6.extend()
    relay7.extend()
    relay8.extend()
    read_all_relay_states()
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
    read_all_relay_states()
    return True

def close_arms():
    # Implement the logic to close the arms using the appropriate relays
    print("Opening arms...")
    # opening arms includes extending the shoulder relays and contracting the arm relays
    relay1.extend()  # lt shoulder relay
    relay2.extend()  # rt shoulder relay
    relay4.contract()  # rt arm relay
    relay7.contract()  # lt arm relay
    return True

def open_arms():
    # Implement the logic to open the arms using the appropriate relays
    print("Closing arms...")
    # opening arms includes extending the shoulder relays and contracting the arm relays
    relay1.contract()  # lt shoulder relay
    relay2.contract()  # rt shoulder relay
    relay4.extend()  # rt arm relay
    relay7.extend()  # lt arm relay
    return True

# Contract then extend a single relay by number (1-8)
def contract_then_extend_relay(relay_num, contract_time=1, extend_time=1):
    if 1 <= relay_num <= 8:
        relay = relays[relay_num - 1]
        print("Contracting relay {}...".format(relay_num))
        relay.contract()
        read_relay_state(relay_num)
        time.sleep(contract_time)
        print("Extending relay {}...".format(relay_num))
        relay.extend()
        read_relay_state(relay_num)
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
        print("4: Read controller state for all relays")
        print("5: Open arms")
        print("6: Close arms")
        print("q: Quit")
        choice = str(input("Select test to run: "))
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
        elif choice == '4':
            read_all_relay_states()
        elif choice == '5':
            open_arms()
        elif choice == '6':
            close_arms()
        elif choice == 'q':
            print("Exiting relay test.")
            break
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main()
