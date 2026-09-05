<<<<<<< HEAD
#!/usr/bin/python3

import time
from relays import *

# Set up relays as in mqtt_cs_and_ec.py
relay1 = LinAct("Coffin Skeleton", 26)
relay2 = LinAct("Electro Closet", 20)
relay3 = LinAct("Electro Closet", 21)

relays = [relay1, relay2, relay3]

def test_individual_relays():
    for idx, relay in enumerate(relays, 1):
        print(f"Relay {idx} ON (extend)")
        relay.extend()
        time.sleep(1)
        print(f"Relay {idx} OFF (contract)")
        relay.contract()
        time.sleep(1)

def test_all_on():
    print("All relays ON (extend)")
    for relay in relays:
        relay.extend()
    time.sleep(1)

def test_all_off():
    print("All relays OFF (contract)")
    for relay in relays:
        relay.contract()
    time.sleep(1)

def main():
    test_individual_relays()
    test_all_on()
    test_all_off()
    print("Relay test complete.")

if __name__ == "__main__":
    main()
=======
#!/usr/bin/python3

import time
from relays import *

# Set up relays as in mqtt_cs_and_ec.py
relay1 = LinAct("Coffin Skeleton", 26)
relay2 = LinAct("Electro Closet", 20)
relay3 = LinAct("Electro Closet", 21)

relays = [relay1, relay2, relay3]

def test_individual_relays():
    for idx, relay in enumerate(relays, 1):
        print(f"Relay {idx} ON (extend)")
        relay.extend()
        time.sleep(1)
        print(f"Relay {idx} OFF (contract)")
        relay.contract()
        time.sleep(1)

def test_all_on():
    print("All relays ON (extend)")
    for relay in relays:
        relay.extend()
    time.sleep(1)

def test_all_off():
    print("All relays OFF (contract)")
    for relay in relays:
        relay.contract()
    time.sleep(1)

def main():
    test_individual_relays()
    test_all_on()
    test_all_off()
    print("Relay test complete.")

if __name__ == "__main__":
    main()
>>>>>>> 8c31b29eda0ad6cdcab8273d6ed029af0993864a
