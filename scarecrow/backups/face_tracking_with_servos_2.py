#!/usr/bin/python3

import cv2
from robot_hat import Servo
from robot_hat.utils import reset_mcu
from time import sleep

# Initialize servos
pan_servo = Servo(8)   # Horizontal movement
tilt_servo = Servo(7)  # Vertical movement

# initialize servos
pan_servo = Servo(8) # horizontal movement
#pan_servo.angle(0)
tilt_servo = Servo(7) # vertical movememtn
#tilt_servo.angle(0)

# Servo angle limits
SERVO_MIN = -45
SERVO_MAX = 45

# Frame dimensions (adjust if needed)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Helper function to map pixel to angle
def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        face_center_x = x + w // 2
        face_center_y = y + h // 2

        # Map face position to servo angles
        # Pan: left (0) → +90, right (640) → -90 (counter-clockwise is positive)
        pan_angle = map_range(face_center_x, 0, FRAME_WIDTH, 45, -45)

        # Tilt: top (0) → +90, bottom (480) → -90 (up is negative)
        tilt_angle = map_range(face_center_y, 0, FRAME_HEIGHT, 45, -45)

        # Set servo angles
        """
        pan_servo.angle(int(pan_angle))
        tilt_servo.angle(int(tilt_angle))
        """

        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Face Tracking', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
