#!/usr/bin/python3

import time

""" 
        front - extend_one    - relay1.extend() 
        back  - contract_one  - relay1.contract() 
        down  - extend_two    - relay2.extend() 
        up    - contract_two  - relay2.contract 

        Sequence:
            back, 5 seconds
            up, 8 seconds
            front, 1 seconds
            back, 1 seconds
            front, 1 seconds
            back, 1 seconds
"""

def zombie_awake(relay1, relay2, strobe): 
    relay1.contract() 
    time.sleep(5)
    relay2.contract()
    time.sleep(10)
    relay1.extend()
    time.sleep(1)
    relay1.contract()
    strobe.contract()
    time.sleep(1)
    relay1.extend()
    time.sleep(2)
    relay1.contract()
    time.sleep(2)
    relay1.extend()
    time.sleep(1)
    relay1.contract()
    strobe.contract()
    time.sleep(1)
    relay1.extend()
    time.sleep(4)
    relay1.contract()
    time.sleep(2)
    relay1.extend()
    time.sleep(1)
    relay1.contract()
    time.sleep(1)
    relay1.extend()
    time.sleep(2)
    relay1.contract()

def zombie_sleep(relay1, relay2, strobe): 
    relay2.extend()
    time.sleep(6)
    strobe.contract()
    relay1.extend()
