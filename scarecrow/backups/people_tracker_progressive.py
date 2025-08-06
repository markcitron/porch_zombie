#!/usr/bin/python3

import cv2
import imutils
import time
import random
import pygame
from robot_hat import Servo

# Initialize servos
pan_servo = Servo(8)
pan_servo.angle(0)
tilt_servo = Servo(7)
tilt_servo.angle(-10)

# take a quick nap before getting started
time.sleep(5)

# Servo angle limits
ANGLE_MIN = -45
ANGLE_MAX = 45

# Frame dimensions
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Smoothing
current_pan = 0
current_tilt = 0

# Motion filtering
MIN_AREA = 3000
ASPECT_RATIO_MIN = 0.3
ASPECT_RATIO_MAX = 1.5

# Patrol mode
patrol_angle = ANGLE_MIN
patrol_direction = 1
patrol_step = 2
last_motion_time = time.time()
motion_timeout = 3  # seconds

# Sound setup
"""
pygame.mixer.init()
pygame.mixer.music.load("scare_sound.mp3")  # Replace with your sound file
"""

# Helper functions
def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def ease_angle(current, target, factor=0.05):
    return current + factor * (target - current)

cap = cv2.VideoCapture(0)
avg = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = imutils.resize(frame, width=FRAME_WIDTH)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if avg is None:
        avg = gray.copy().astype("float")
        continue

    cv2.accumulateWeighted(gray, avg, 0.5)
    frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    motion_center = None

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < MIN_AREA:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        if not (ASPECT_RATIO_MIN <= aspect_ratio <= ASPECT_RATIO_MAX):
            continue
        motion_center = (x + w // 2, y + h // 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        break

    if motion_center:
        last_motion_time = time.time()
        cx, cy = motion_center

        target_pan = map_range(cx, 0, FRAME_WIDTH, ANGLE_MAX, ANGLE_MIN)
        target_tilt = map_range(cy, 0, FRAME_HEIGHT, ANGLE_MIN, ANGLE_MAX)

        current_pan = ease_angle(current_pan, target_pan)
        current_tilt = ease_angle(current_tilt, target_tilt)

        pan_servo.angle(current_pan)
        tilt_servo.angle(current_tilt)

        # Play sound if not already playing
        """
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        """

    else:
        if time.time() - last_motion_time > motion_timeout:
            if random.random() < 0.02:
                time.sleep(random.uniform(0.5, 1.5))  # Random pause

            patrol_angle += patrol_direction * patrol_step
            if patrol_angle >= ANGLE_MAX or patrol_angle <= ANGLE_MIN:
                patrol_direction *= -1
                patrol_angle = max(min(patrol_angle, ANGLE_MAX), ANGLE_MIN)

            pan_servo.angle(patrol_angle)
            tilt_servo.angle(0)

    cv2.imshow("Scarecrow Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
