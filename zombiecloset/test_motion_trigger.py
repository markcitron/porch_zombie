#!/usr/bin/python3
"""Display raw motion sensor state, transitions, and state durations."""

import time

import RPi.GPIO as GPIO

PIR_PIN = 5  # BCM numbering for physical pin 29
SAMPLE_INTERVAL = 0.02
STATUS_INTERVAL = 1.0


def state_name(state):
    return "HIGH" if state == GPIO.HIGH else "LOW"


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    previous_state = GPIO.input(PIR_PIN)
    state_started = time.monotonic()
    next_status = state_started

    print(
        f"Monitoring raw motion signal on BCM {PIR_PIN} "
        "(physical pin 29)."
    )
    print("Move in front of the sensor and watch for state changes.")
    print("Press Ctrl+C to stop.")
    print(f"Initial state: {state_name(previous_state)}", flush=True)

    try:
        while True:
            current_state = GPIO.input(PIR_PIN)
            now = time.monotonic()

            if current_state != previous_state:
                duration = now - state_started
                print(
                    f"TRANSITION: {state_name(previous_state)} -> "
                    f"{state_name(current_state)} "
                    f"(previous state lasted {duration:.3f}s)",
                    flush=True,
                )
                previous_state = current_state
                state_started = now

            if now >= next_status:
                duration = now - state_started
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"{timestamp} - RAW {state_name(current_state)} "
                    f"(held for {duration:.1f}s)",
                    flush=True,
                )
                next_status = now + STATUS_INTERVAL

            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup(PIR_PIN)


if __name__ == "__main__":
    main()
