#!/usr/bin/python3

# enhanced_scarecrow_motion.py

import time
import random
import threading
from robot_hat import Servo

# --- Servo Setup ---
PAN_MIN = -45
PAN_MAX = 45
TILT_MIN = -20
TILT_MAX = 20
PAN_NEUTRAL = 0
TILT_NEUTRAL = 0

pan_servo = Servo(8)
tilt_servo = Servo(7)

def set_pan(angle_deg):
    angle_deg = max(PAN_MIN, min(PAN_MAX, angle_deg))
    pan_servo.angle(angle_deg)

def set_tilt(angle_deg):
    angle_deg = max(TILT_MIN, min(TILT_MAX, angle_deg))
    tilt_servo.angle(angle_deg)

def smooth_move_servo(set_func, start, end, step=2, delay=0.05):
    direction = 1 if end > start else -1
    for angle in range(int(start), int(end), direction * step):
        set_func(angle + random.uniform(-0.5, 0.5))
        time.sleep(delay)
    set_func(end)

def pan_sweep():
    while True:
        smooth_move_servo(set_pan, PAN_MIN, PAN_MAX, step=3, delay=0.04)
        time.sleep(random.uniform(0.2, 0.5))

        # Random chance to interrupt with tilt
        if random.random() < 0.3:
            tilt_sequence()

        smooth_move_servo(set_pan, PAN_MAX, PAN_MIN, step=3, delay=0.04)
        time.sleep(random.uniform(0.2, 0.5))

        if random.random() < 0.3:
            tilt_sequence()

def tilt_sequence():
    smooth_move_servo(set_tilt, TILT_NEUTRAL, TILT_MIN, step=2, delay=0.05)
    time.sleep(random.uniform(0.2, 0.4))
    smooth_move_servo(set_tilt, TILT_MIN, TILT_MAX, step=2, delay=0.05)
    time.sleep(random.uniform(0.2, 0.4))
    smooth_move_servo(set_tilt, TILT_MAX, TILT_NEUTRAL, step=2, delay=0.05)

def idle_tilt_loop():
    while True:
        # Gentle breathing-like nods
        offset = random.randint(-5, 5)
        smooth_move_servo(set_tilt, TILT_NEUTRAL, TILT_NEUTRAL + offset, step=1, delay=0.06)
        time.sleep(random.uniform(1.0, 2.0))
        smooth_move_servo(set_tilt, TILT_NEUTRAL + offset, TILT_NEUTRAL, step=1, delay=0.06)
        time.sleep(random.uniform(1.0, 2.0))

# --- Main Loop ---
try:
    print("🧟 Enhanced scarecrow motion active...")

    # Start pan sweep and idle tilt in parallel
    pan_thread = threading.Thread(target=pan_sweep)
    tilt_thread = threading.Thread(target=idle_tilt_loop)

    pan_thread.start()
    tilt_thread.start()

    pan_thread.join()
    tilt_thread.join()

except KeyboardInterrupt:
    print("🛑 Shutting down scarecrow motion...")

finally:
    pan_servo.release()
    tilt_servo.release()
