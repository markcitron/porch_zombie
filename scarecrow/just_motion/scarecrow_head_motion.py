#!/usr/bin/python3

# scarecrow_head_motion.py

import time
import random
from robot_hat import Servo

# --- Servo Setup ---
PAN_MIN = -90
PAN_MAX = 90
TILT_MIN = -45
TILT_MAX = 45
PAN_NEUTRAL = 0
TILT_NEUTRAL = 0

pan_servo = Servo(8)   # left/right
tilt_servo = Servo(7)  # up/down

def set_pan(angle_deg):
    angle_deg = max(PAN_MIN, min(PAN_MAX, angle_deg))
    pan_servo.angle(angle_deg)

def set_tilt(angle_deg):
    angle_deg = max(TILT_MIN, min(TILT_MAX, angle_deg))
    tilt_servo.angle(angle_deg)

def look_around():
    # Sweep left to right with pauses
    for angle in range(PAN_MIN, PAN_MAX + 1, 15):
        set_pan(angle + random.uniform(-3, 3))  # add jitter
        set_tilt(TILT_NEUTRAL + random.uniform(-2, 2))
        time.sleep(random.uniform(0.3, 0.6))

    time.sleep(0.5)

    # Sweep right to left
    for angle in range(PAN_MAX, PAN_MIN - 1, -15):
        set_pan(angle + random.uniform(-3, 3))
        set_tilt(TILT_NEUTRAL + random.uniform(-2, 2))
        time.sleep(random.uniform(0.3, 0.6))

def look_up_down():
    # Look up slowly
    for angle in range(TILT_NEUTRAL, TILT_MIN - 1, -5):
        set_tilt(angle)
        time.sleep(0.2)

    time.sleep(0.5)

    # Look down slowly
    for angle in range(TILT_MIN, TILT_MAX + 1, 5):
        set_tilt(angle)
        time.sleep(0.2)

    time.sleep(0.5)

    # Return to neutral
    set_tilt(TILT_NEUTRAL)
    time.sleep(0.5)

# --- Main Loop ---
try:
    print("🧟 Scarecrow idle motion active...")
    while True:
        look_around()
        look_up_down()
        time.sleep(random.uniform(1.0, 2.0))

except KeyboardInterrupt:
    print("🛑 Shutting down scarecrow motion...")

finally:
    pan_servo.release()
    tilt_servo.release()
