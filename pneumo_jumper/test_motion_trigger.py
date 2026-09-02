#!/usr/bin/python 

import RPi.GPIO as GPIO
import time

PIR_PIN = 5  # BCM numbering for pin 29

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

MIN_TRIGGER_TIME = 0.30   # seconds of sustained motion required
COOLDOWN = 2.0            # ignore new triggers for 2 seconds

last_trigger = 0

print("Filtered PIR Test Running...")

try:
    while True:
        now = time.time()

        # Cooldown window
        if now - last_trigger < COOLDOWN:
            time.sleep(0.05)
            continue

        # If PIR goes HIGH, measure how long it stays HIGH
        if GPIO.input(PIR_PIN):
            start = time.time()
            while GPIO.input(PIR_PIN):
                time.sleep(0.01)
            duration = time.time() - start

            if duration >= MIN_TRIGGER_TIME:
                print(f"Valid motion! Duration: {duration:.2f}s")
                last_trigger = time.time()
            else:
                print(f"Ignored small motion ({duration:.2f}s)")

        time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Exiting...")
