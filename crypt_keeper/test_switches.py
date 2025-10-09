#!/usr/bin/python3

import time
from gpiozero import LED

relay_1 = LED(5)
relay_2 = LED(6)
relay_3 = LED(13)
relay_4 = LED(19)
relay_5 = LED(26)
relay_6 = LED(21)
relay_7 = LED(20)
relay_8 = LED(16)

relays = [relay_1, relay_2, relay_3, relay_4, relay_5, relay_6, relay_7, relay_8]

WAIT = 0.5  # seconds between actions

# turn them on one at a time
def test_individual_relays():
    for idx, relay in enumerate(relays, 1):
        print(f"Relay {idx} ON (extend)")
        relay.on()
        time.sleep(WAIT)
        print(f"Relay {idx} OFF (contract)")
        relay.off()
        time.sleep(WAIT)

# turn them all on, then off
def test_all_on():
    print("All relays ON (extend)")
    for relay in relays:
        relay.on()
    time.sleep(WAIT)

    print("All relays OFF (contract)")
    for relay in relays:
        relay.off()
    time.sleep(WAIT)

def main():
    test_individual_relays()
    test_all_on()
    print("Relay test complete.")   

if __name__ == "__main__":
    main()  