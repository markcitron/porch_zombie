#!/usr/bin/python3

# creepy_skull_idle_safe.py

import time
import random
from robot_hat import Servo

# --- Servo Setup ---
PAN_MIN = -45
PAN_MAX = 45
TILT_MIN = -15
TILT_MAX = 15
PAN_NEUTRAL = 0
TILT_NEUTRAL = 0

pan_servo = Servo(8)   # left/right
tilt_servo = Servo(7)  # up/down

def set_pan(angle_deg):
    clamped = max(PAN_MIN, min(PAN_MAX, angle_deg))
    if angle_deg != clamped:
        print(f"⚠️ Pan angle {angle_deg:.2f} clamped to {clamped:.2f}")
    pan_servo.angle(clamped)

def set_tilt(angle_deg):
    clamped = max(TILT_MIN, min(TILT_MAX, angle_deg))
    if angle_deg != clamped:
        print(f"⚠️ Tilt angle {angle_deg:.2f} clamped to {clamped:.2f}")
    tilt_servo.angle(clamped)

# --- Motion Profile ---
class MotionProfile:
    def __init__(self, pan_step=1, tilt_step=1, delay=0.08, drift=0.3):
        self.pan_step = pan_step
        self.tilt_step = tilt_step
        self.delay = delay
        self.drift = drift

profile = MotionProfile(pan_step=1, tilt_step=1, delay=0.08, drift=0.3)

def smooth_move_servo(set_func, start, end, step, delay, drift):
    direction = 1 if end > start else -1
    for angle in range(int(start), int(end), direction * step):
        drifted = angle + random.uniform(-drift, drift)
        set_func(drifted)
        time.sleep(delay)
    set_func(end)

def eerie_tilt_scan():
    smooth_move_servo(set_tilt, TILT_NEUTRAL, TILT_MIN, profile.tilt_step, profile.delay, profile.drift)
    time.sleep(random.uniform(0.4, 0.7))

    smooth_move_servo(set_tilt, TILT_MIN, TILT_MAX, profile.tilt_step, profile.delay, profile.drift)
    time.sleep(random.uniform(0.4, 0.7))

    final_tilt = TILT_NEUTRAL + random.uniform(-1.5, 1.5)
    set_tilt(final_tilt)

def eerie_idle_motion():
    global last_pan
    pan_targets = list(range(PAN_MIN, PAN_MAX + 1, 10))
    random.shuffle(pan_targets)

    for target in pan_targets:
        if abs(target - last_pan) < 10:
            continue

        smooth_move_servo(set_pan, last_pan, target, profile.pan_step, profile.delay, profile.drift)
        last_pan = target
        time.sleep(random.uniform(0.3, 0.6))

        if random.random() < 0.4:
            eerie_tilt_scan()

        if random.random() < 0.2:
            twitch_angle = max(PAN_MIN, min(PAN_MAX, target + random.uniform(-2, 2)))
            set_pan(twitch_angle)
            time.sleep(random.uniform(0.2, 0.4))

# --- Main Loop ---
last_pan = PAN_NEUTRAL

try:
    print("💀 Creepy skull idle motion active...")
    set_pan(PAN_NEUTRAL)
    set_tilt(TILT_NEUTRAL)
    while True:
        eerie_idle_motion()
        time.sleep(random.uniform(2.0, 4.0))

except KeyboardInterrupt:
    print("🛑 Shutting down skull motion...")
