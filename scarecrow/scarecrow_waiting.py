#!/usr/bin/python3
"""Grab nearby visitors while the scarecrow's base relay is enabled."""

import math
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from robot_hat import Pin, Ultrasonic

from scarecrow_actions import (
    HandController,
    WristController,
    initialize_hardware,
    read_relay_state,
)
from test_actions import grab, let_go
from test_distance_ultra import ECHO_PIN, READ_INTERVAL, TRIGGER_PIN

BASE_RELAY = 6
TRIGGER_DISTANCE_CM = 50.0
STARTUP_DELAY_SECONDS = 15.0
HOLD_SECONDS = 5.0


def monitor_base_relay(stop: Event) -> None:
    """Latch a shutdown request even while a blocking action is running."""
    try:
        while not stop.is_set():
            state = read_relay_state(BASE_RELAY)
            if state not in (0, 1):
                raise RuntimeError(
                    f"Unexpected relay {BASE_RELAY} state: {state!r}"
                )
            if state == 0:
                print("Base relay is off. Releasing and exiting.", flush=True)
                return
            stop.wait(READ_INTERVAL)
    finally:
        # Wake the main thread on relay-off or a failed controller read.
        stop.set()


def main() -> None:
    initialize_hardware()
    hand_controller = HandController()
    wrist_controller = WristController()
    stop = Event()

    with ThreadPoolExecutor(max_workers=1) as executor:
        monitor = executor.submit(monitor_base_relay, stop)
        try:
            ultrasonic = Ultrasonic(Pin(TRIGGER_PIN), Pin(ECHO_PIN))
            print(
                f"Waiting {STARTUP_DELAY_SECONDS:g} seconds before "
                "watching for visitors...",
                flush=True,
            )
            if stop.wait(STARTUP_DELAY_SECONDS):
                return

            armed = True
            while not stop.is_set():
                distance = ultrasonic.read()
                if stop.is_set():
                    break

                if not math.isfinite(distance) or distance < 0:
                    print(
                        f"Invalid ultrasonic reading ({distance!r}); "
                        "check sensor power and TRIG/ECHO wiring.",
                        flush=True,
                    )
                elif distance > TRIGGER_DISTANCE_CM:
                    armed = True
                elif armed:
                    armed = False
                    print(f"Visitor at {distance:.2f} cm. Grabbing.", flush=True)
                    grab(hand_controller, wrist_controller)
                    if stop.wait(HOLD_SECONDS):
                        break
                    let_go(hand_controller, wrist_controller)

                stop.wait(READ_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopping scarecrow.", flush=True)
        finally:
            stop.set()
            try:
                let_go(hand_controller, wrist_controller)
            finally:
                # Propagate monitor failures rather than silently exiting.
                monitor.result()


if __name__ == "__main__":
    main()