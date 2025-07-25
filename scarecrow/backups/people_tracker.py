#!/usr/bin/python3

import cv2
import time
import numpy as np
from gpiozero import Servo
from simple_pid import PID  # optional for smoothing

# Servo setup (adjust GPIO pins as needed)
pan_servo = Servo(17)
tilt_servo = Servo(18)

# Video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Parameters
dead_zone = 30
min_contour_area = 1000
frame_center = (160, 120)
motion_history = []

def map_position(value, max_pixels):
    return (value / max_pixels) * 2 - 1  # map to [-1, 1] for Servo

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Prepare frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # First frame logic
    if 'prev_frame' not in locals():
        prev_frame = gray
        continue

    # Motion detection
    diff = cv2.absdiff(prev_frame, gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    prev_frame = gray

    targets = []
    for c in contours:
        if cv2.contourArea(c) > min_contour_area:
            x, y, w, h = cv2.boundingRect(c)
            cx = x + w // 2
            cy = y + h // 2
            targets.append((cx, cy))
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if targets:
        avg_cx = sum(p[0] for p in targets) // len(targets)
        avg_cy = sum(p[1] for p in targets) // len(targets)

        dx = avg_cx - frame_center[0]
        dy = avg_cy - frame_center[1]

        # Dead zone filtering
        if abs(dx) > dead_zone:
            pan_servo.value = map_position(avg_cx, 320)

        if abs(dy) > dead_zone:
            tilt_servo.value = map_position(avg_cy, 240)

    # Display
    cv2.imshow("Motion Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
