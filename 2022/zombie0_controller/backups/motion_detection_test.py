#!/usr/bin/python3

import cv2,time
from datetime import datetime

Video=cv2.VideoCapture(0)
First_Frame=None

while True:
    Check,frame=Video.read()
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray=cv2.GaussianBlur(gray,(21,21),0)
    if First_Frame is None:
        First_Frame=gray
        continue
    delta_frame=cv2.absdiff(First_Frame,gray)
    Threshold_frame=cv2.threshold(delta_frame,50,255,cv2.THRESH_BINARY)[1]
    Threshold_frame=cv2.dilate(Threshold_frame,None,iterations=2)
    (cntr,_)=cv2.findContours(Threshold_frame.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for contour in cntr:
        if cv2.contourArea(contour)>900:
            continue
        (x,y,w,h)=cv2.boundingRect(contour)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)

        dt = datetime.now()
        ts = datetime.timestamp(dt)
        print("{0} Motion detected".format(ts))

    # cv2.imshow('Frame',frame)
    Key=cv2.waitKey(1)
    if Key == ord('q'):
        break

Video.release()
cv2.destroyAllWindows()
