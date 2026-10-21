#!/usr/bin/python3
"""Continuously display the raw output of an HC-SR501-compatible PIR."""

import time
from datetime import datetime

import RPi.GPIO as GPIO

PIR_PIN = 6  # BCM GPIO 6, physical header pin 31
READ_INTERVAL_SECONDS = 0.2


def main() -> None:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)

    try:
        print(
            f"Reading PIR on BCM GPIO {PIR_PIN} (physical pin 31). "
            "Press Ctrl+C to stop.",
            flush=True,
        )
        print(
            "Allow 30-60 seconds after sensor power-up for stabilization; "
            "startup readings may fluctuate.",
            flush=True,
        )
        print(
            "Jumper L: non-retriggering mode. LOW between pulses does not "
            "necessarily mean the person has left.",
            flush=True,
        )

        while True:
            value = GPIO.input(PIR_PIN)
            status = "HIGH - motion signaled" if value else "LOW - idle output"
            timestamp = datetime.now().isoformat(timespec="milliseconds")
            print(f"{timestamp} PIR={value} ({status})", flush=True)
            time.sleep(READ_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nExiting PIR test.", flush=True)
    finally:
        GPIO.cleanup(PIR_PIN)


if __name__ == "__main__":
    main()