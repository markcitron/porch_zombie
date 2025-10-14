#!/usr/bin/python3
"""
Simple PIR sensor test script.

Usage:
  python3 test_pir.py [pin]

- Default GPIO pin is 17 (as used by the main trigger script).
- The script prints motion events and timestamps and runs until interrupted.
"""
import sys
import time

try:
    from gpiozero import MotionSensor
except Exception as e:
    print("gpiozero.MotionSensor is not available:", e)
    print("Install on Raspberry Pi with: sudo apt install python3-gpiozero")
    sys.exit(1)

pin = 23 
if len(sys.argv) > 1:
    try:
        pin = int(sys.argv[1])
    except ValueError:
        print("Invalid pin argument, using default 17")

print(f"Initializing PIR sensor on GPIO{pin}...")

pir = MotionSensor(pin)

print("Ready. Waiting for motion. Press Ctrl-C to exit.")

try:
    while True:
        pir.wait_for_motion()
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"[{ts}] Motion detected!")
        # You can also test wait_for_no_motion or use .when_motion/
        pir.wait_for_no_motion()
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"[{ts}] Motion cleared.")
except KeyboardInterrupt:
    print('\nExiting on user interrupt')
finally:
    try:
        pir.close()
    except Exception:
        pass
