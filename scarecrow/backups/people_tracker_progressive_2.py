#!/usr/bin/python3

import cv2
import imutils
import time
import random
import pygame
from robot_hat import Servo

# 🛠️ Servo Initialization (robot_hat library)
# Pan Servo on port 8: +45 = counterclockwise (left), -45 = clockwise (right)
# Tilt Servo on port 7: -45 = upward, +45 = downward
pan_servo = Servo(8)
tilt_servo = Servo(7)
# set them to center to start
# if there is an offset, adjust here
pan_servo.angle(0)
tilt_servo.angle(0)

# 🎚️ Servo angle limits
ANGLE_MIN = -45    # Most clockwise (pan), most upward (tilt)
ANGLE_MAX = 45     # Most counterclockwise (pan), most downward (tilt)

# 📐 Video frame dimensions (match to your camera resolution)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# 🎛️ Motion filtering
MIN_AREA = 3000                 # Minimum contour area to count as human-sized motion
ASPECT_RATIO_MIN = 0.3         # Exclude long horizontal contours (e.g., waving arms)
ASPECT_RATIO_MAX = 1.5         # Exclude tall narrow contours (e.g., vertical poles)

# 🧁 Smoothing for natural movement
current_pan = 0                # Start servo centered
current_tilt = 0

# 🕵️ Patrol behavior settings
patrol_angle = ANGLE_MIN       # Start patrol at far left
patrol_direction = 1           # +1 = left → right, -1 = right → left
motion_timeout = 3             # Time in seconds before patrol starts
last_motion_time = time.time() # Timestamp of last detected motion

# 🔊 Sound setup (triggered on motion detection)
pygame.mixer.init()
pygame.mixer.music.load("scare_sound.mp3")  # Replace with your scary sound file

# 🔧 Helper: Map pixel coordinates to servo angles
def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)  # Clamp input
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# 🔧 Helper: Smooth transition between angles (easing factor controls softness)
def ease_angle(current, target, factor):
    return current + factor * (target - current)

# 🎥 Start camera capture
cap = cv2.VideoCapture(0)
avg = None  # Used for motion detection via frame averaging

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize and preprocess frame
    frame = imutils.resize(frame, width=FRAME_WIDTH)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Initialize average frame on first iteration
    if avg is None:
        avg = gray.copy().astype("float")
        continue

    # 🧠 Motion detection logic
    cv2.accumulateWeighted(gray, avg, 0.5)
    frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    motion_center = None  # Coordinates of valid movement

    # 🕵️ Filter contours to find large, human-like motion
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
        break  # Only track the first valid target

    if motion_center:
        # 🎯 Lock onto motion and trigger tracking response
        last_motion_time = time.time()
        cx, cy = motion_center

        # Map frame center to servo angle ranges
        target_pan = map_range(cx, 0, FRAME_WIDTH, ANGLE_MAX, ANGLE_MIN)
        target_tilt = map_range(cy, 0, FRAME_HEIGHT, ANGLE_MIN, ANGLE_MAX)

        # Smoother movement when actively tracking
        current_pan = ease_angle(current_pan, target_pan, factor=0.1)   # Faster easing
        current_tilt = ease_angle(current_tilt, target_tilt, factor=0.1)

        pan_servo.angle(current_pan)
        tilt_servo.angle(current_tilt)

        # Trigger sound effect if not already playing
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

    else:
        # 🤖 Patrol mode if no motion recently
        idle_duration = time.time() - last_motion_time
        if idle_duration > motion_timeout:
            # Adjust patrol speed based on how long it's been idle
            patrol_step = 1 if idle_duration > 10 else 3

            # Add randomized pause for lifelike idling
            if random.random() < 0.02:
                time.sleep(random.uniform(0.5, 1.5))  # Simulate hesitation or curiosity

            # Sweep the pan servo back and forth
            patrol_angle += patrol_direction * patrol_step
            if patrol_angle >= ANGLE_MAX or patrol_angle <= ANGLE_MIN:
                patrol_direction *= -1
                patrol_angle = max(min(patrol_angle, ANGLE_MAX), ANGLE_MIN)

            pan_servo.angle(patrol_angle)
            tilt_servo.angle(0)  # Neutral tilt during idle sweep

    # 💻 Preview window (can be disabled for headless operation)
    cv2.imshow("Scarecrow Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 🧹 Cleanup
cap.release()
cv2.destroyAllWindows()
