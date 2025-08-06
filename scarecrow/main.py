#!/usr/bin/python3

import cv2
from orientation import get_servo_angles
from smoothing import smooth_angle

# Optional: import config and use values dynamically

prev_pan = 0
prev_tilt = 0

def update_servos(pan, tilt):
    print(f"Moving to pan: {pan}, tilt: {tilt}")
    # Your servo control calls here

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Example: find motion or face and get center (x, y)
    # For demo, assume center
    x = frame.shape[1] // 2
    y = frame.shape[0] // 2

    pan, tilt = get_servo_angles(x, y)
    pan = smooth_angle(prev_pan, pan)
    tilt = smooth_angle(prev_tilt, tilt)

    update_servos(pan, tilt)

    prev_pan = pan
    prev_tilt = tilt

cap.release()
