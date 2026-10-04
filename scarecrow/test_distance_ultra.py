#!/usr/bin/python3
"""Continuously test an ultrasonic sensor connected to the Robot HAT."""

import time

from robot_hat import Pin, Ultrasonic

TRIGGER_PIN = "D2"
ECHO_PIN = "D3"
READ_INTERVAL = 0.2


def main():
    ultrasonic = Ultrasonic(Pin(TRIGGER_PIN), Pin(ECHO_PIN))

    print(
        f"Reading ultrasonic sensor: TRIG={TRIGGER_PIN}, "
        f"ECHO={ECHO_PIN}. Press Ctrl+C to stop."
    )

    try:
        while True:
            distance = ultrasonic.read()
            if distance == -1:
                print(
                    "No echo received (timeout). Check sensor power, "
                    "TRIG/ECHO wiring, and pin selection.",
                    flush=True,
                )
            else:
                print(f"Distance: {distance:.2f} cm", flush=True)

            time.sleep(READ_INTERVAL)
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()
