#!/usr/bin/python3

import cv2
import imutils
from robot_hat import Servo, ADC
from robot_hat.utils import reset_mcu
from time import sleep

print("Resetting MCU...")
reset_mcu()
sleep(1)

adc0 = ADC(0)
adc1 = ADC(1)
adc2 = ADC(2)
adc3 = ADC(3)
adc4 = ADC(4)

# Initialize servos
print("Resetting servos ...")
pan_servo = Servo(8)
pan_servo.angle(0) # set initial pan angle to 0
tilt_servo = Servo(7)
tilt_servo.angle(0) # set initial tilt angle to 0
sleep(3)

SERVO_MIN = -45
SERVO_MAX = 45
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

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

    # Compute frame difference
    cv2.accumulateWeighted(gray, avg, 0.5)
    frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Find contours
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    motion_center = None

    for contour in contours:
        if cv2.contourArea(contour) < 2000:
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        motion_center = (x + w // 2, y + h // 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        break  # Track only the first significant motion

    if motion_center:
        (cx, cy) = motion_center
        pan_angle = map_range(cx, 0, FRAME_WIDTH, 45, -45)
        tilt_angle = map_range(cy, 0, FRAME_HEIGHT, -45, 45)
        pan_servo.angle(pan_angle)
        tilt_servo.angle(tilt_angle)

    """ 
    cv2.imshow("Motion Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    """ 

cap.release()
cv2.destroyAllWindows()
