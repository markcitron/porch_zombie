#!/usr/bin/python3
"""Control the Zombie Closet solenoid."""

import time

from relays import LinAct

ZOMBIE_CLOSET_PIN = 26
ACTIVATION_TIME = 10.0

SIDEKICK_PIN = 27

_closet_relay = LinAct("Zombie Closet", ZOMBIE_CLOSET_PIN)
_sidekick_relay = LinAct("Sidekick", SIDEKICK_PIN)


def open_closet():
    """Open the Zombie Closet."""
    print("Opening Zombie Closet")
    _closet_relay.contract()


def close_closet():
    """Close the Zombie Closet."""
    print("Closing Zombie Closet")
    _closet_relay.extend()


def activate_zc():
    """Open the Zombie Closet for ten seconds, then close it."""
    open_closet()
    try:
        time.sleep(ACTIVATION_TIME)
    finally:
        close_closet()

def activate_sidekick():
    """Activate the Sidekick solenoid for ten seconds."""
    print("Activating Sidekick")
    _sidekick_relay.extend()
    try:
        time.sleep(ACTIVATION_TIME)
    finally:
        _sidekick_relay.contract()
