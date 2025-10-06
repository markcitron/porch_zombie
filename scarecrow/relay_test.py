#!/usr/bin/python

import time
import lib8relind

# set up linear actuator relays
relay1 = LinAct("", 1)
relay2 = LinAct("", 2)
relay3 = LinAct("", 3)
relay4 = LinAct("", 4)
relay5 = LinAct("", 5)
relay6 = LinAct("", 6)
relay7 = LinAct("", 7)
relay8 = LinAct("", 8)

def trigger_relay(relay):
    print(f"Extending relay {relay}!")
    relay.extend()
    time.sleep(1)
    print(f"Contracting relay {relay}!")
    relay.contract()
    time.sleep(1)
    return True

def main():
    print("Testing scarecrow relays...")
    trigger_relay(relay1)
    trigger_relay(relay2)
    trigger_relay(relay3)
    trigger_relay(relay4)
    trigger_relay(relay5)
    trigger_relay(relay6)
    trigger_relay(relay7)
    trigger_relay(relay8)
    return True

if __name__ == "__main__":
    main()
