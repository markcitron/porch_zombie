#!/usr/bin/python3
"""Control the Zombie Closet solenoid."""

import time

from relays import LinAct

ZOMBIE_CLOSET_PIN = 26
ACTIVATION_TIME = 10.0

_closet_relay = LinAct("Zombie Closet", ZOMBIE_CLOSET_PIN)


def open_closet():
    """Open the Zombie Closet."""
    print("Opening Zombie Closet")
    _closet_relay.contract()


def close_closet():
    """Close the Zombie Closet."""
    print("Closing Zombie Closet")
    _closet_relay.extend()


def activate():
    """Open the Zombie Closet for ten seconds, then close it."""
    open_closet()
    try:
        time.sleep(ACTIVATION_TIME)
    finally:
        close_closet()
