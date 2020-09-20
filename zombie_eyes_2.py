#!/usr/bin/python3

from picamera.array import PiRBGArray
from picamera import PiCamera
import time
import cv2
from time import sleep

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

camera = PiCamera()
width, height = 320, 240
camera.resolution = (width, height)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(width, height))
time.sleep(1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        frame = cv2.flip(iamge, 1)

gray = cv2.vctColor(frame, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, 1.3, 5)
c = 0
for(x,y,wq,h) in faces:
    c += 1
    if (c > 1):
        break

cv2.imshow('famee', frame)

