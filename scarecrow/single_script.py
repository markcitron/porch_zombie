#!/usr/bin/python3

import cv2
import imutils
import time
import random
import pygame
from robot_hat import Servo

# 🛠️ Servo Setup
pan_servo = Servo(8)   # Pan: left/right
tilt_servo = Servo(7)  # Tilt: up/down

# 🎚️ Servo Angle Limits
PAN_MIN = -90
PAN_MAX = 90
TILT_MIN = -45
TILT_MAX = 45

# 📐 Frame Dimensions (camera-dependent)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# 🕵️ Motion Filtering Parameters
MIN_AREA = 3000
ASPECT_RATIO_MIN = 0.3
ASPECT_RATIO_MAX = 1.5

# 🎛️ Smoothing Variables
current_pan = 0
current_tilt = 0

# 👁️ Patrol Mode Variables
patrol_angle = PAN_MIN
patrol_direction = 1
motion_timeout = 3
last_motion_time = time.time()

# 🔊 Multi-Zone Sounds
"""
pygame.mixer.init()
left_sound = pygame.mixer.Sound("growl.wav")
center_sound = pygame.mixer.Sound("laugh.wav")
right_sound = pygame.mixer.Sound("chains.wav")
"""

# 🔧 Mapping and Easing
def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def ease_angle(current, target, factor):
    return current + factor * (target - current)

# 🧠 Zone Detection
"""
def trigger_sound_by_zone(cx):
    if cx < FRAME_WIDTH // 3:
        left_sound.play()
    elif cx < 2 * FRAME_WIDTH // 3:
        center_sound.play()
    else:
        right_sound.play()
"""

# 🎥 Video Stream
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

        target_pan = map_range(cx, 0, FRAME_WIDTH, PAN_MAX, PAN_MIN)
        target_tilt = map_range(cy, 0, FRAME_HEIGHT, TILT_MIN, TILT_MAX)

        current_pan = ease_angle(current_pan, target_pan, factor=0.1)
        current_tilt = ease_angle(current_tilt, target_tilt, factor=0.1)

        pan_servo.angle(current_pan)
        tilt_servo.angle(current_tilt)

        # commenting out sound for now, it isn't working, need to reinstall the pygame module
        # trigger_sound_by_zone(cx)

    else:
        idle_duration = time.time() - last_motion_time
        if idle_duration > motion_timeout:
            patrol_step = 1 if idle_duration > 10 else 3

            if random.random() < 0.02:
                time.sleep(random.uniform(0.5, 1.5))

            patrol_angle += patrol_direction * patrol_step
            if patrol_angle >= PAN_MAX or patrol_angle <= PAN_MIN:
                patrol_direction *= -1
                patrol_angle = max(min(patrol_angle, PAN_MAX), PAN_MIN)

            pan_servo.angle(patrol_angle)
            tilt_servo.angle(0)

    # headless running
    # cv2.imshow("Scarecrow Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 🧹 Shutdown
cap.release()
cv2.destroyAllWindows()
