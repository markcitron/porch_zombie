#!/home/pi/repos/porch_zombie/venv/bin/pyhthon

import cv2
import numpy as np

# Parameters
CAMERA_INDEX = 0  # Default USB camera
MIN_AREA = 5000   # Minimum area for motion to be considered

cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("Could not open camera.")
    exit(1)

print("Press 'q' to quit.")

ret, frame1 = cap.read()
ret, frame2 = cap.read()

while ret:
    # Compute absolute difference between frames
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False
    for contour in contours:
        if cv2.contourArea(contour) < MIN_AREA:
            continue
        motion_detected = True
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)

    if motion_detected:
        cv2.putText(frame1, "Motion Detected!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("USB Camera Motion Test", frame1)
    frame1 = frame2
    ret, frame2 = cap.read()

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
