#!/usr/bin/python3
"""Control the Zombie Closet solenoid."""

import time

from relays import LinAct

ZOMBIE_CLOSET_PIN = 26
ZC_ACTIVATION_TIME = 10.0

SIDEKICK_PIN = 20
SIDEKICK_ACTIVATION_TIME = 10.0


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
        time.sleep(ZC_ACTIVATION_TIME)
    finally:
        close_closet()

def activate_sidekick():
    """Activate the Sidekick solenoid for ten seconds."""
    print("Activating Sidekick")
    _sidekick_relay.contract()
    try:
        time.sleep(SIDEKICK_ACTIVATION_TIME)
    except Exception as e:
        print(f"Error occurred while activating Sidekick: {e}")
    finally:
        _sidekick_relay.extend()
