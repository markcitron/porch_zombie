#!/usr/bin/python3

# smooth_scarecrow_head.py

import time
import random
from robot_hat import Servo

# --- Servo Setup ---
PAN_MIN = -90
PAN_MAX = 90
TILT_MIN = -20
TILT_MAX = 20
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

def smooth_move_servo(set_func, start, end, step=2, delay=0.05):
    direction = 1 if end > start else -1
    for angle in range(int(start), int(end), direction * step):
        set_func(angle + random.uniform(-0.5, 0.5))  # subtle drift
        time.sleep(delay)
    set_func(end)

def look_around():
    # Sweep left to right
    smooth_move_servo(set_pan, PAN_MIN, PAN_MAX, step=3, delay=0.04)
    time.sleep(random.uniform(0.3, 0.6))

    # Sweep right to left
    smooth_move_servo(set_pan, PAN_MAX, PAN_MIN, step=3, delay=0.04)
    time.sleep(random.uniform(0.3, 0.6))

def look_up_down():
    # Look up
    smooth_move_servo(set_tilt, TILT_NEUTRAL, TILT_MIN, step=2, delay=0.05)
    time.sleep(random.uniform(0.3, 0.5))

    # Look down
    smooth_move_servo(set_tilt, TILT_MIN, TILT_MAX, step=2, delay=0.05)
    time.sleep(random.uniform(0.3, 0.5))

    # Return to neutral
    smooth_move_servo(set_tilt, TILT_MAX, TILT_NEUTRAL, step=2, delay=0.05)

# --- Main Loop ---
try:
    print("🧟 Smooth scarecrow idle motion active...")
    while True:
        look_around()
        look_up_down()
        time.sleep(random.uniform(1.0, 2.0))

except KeyboardInterrupt:
    print("🛑 Shutting down scarecrow motion...")

finally:
    pan_servo.release()
    tilt_servo.release()
