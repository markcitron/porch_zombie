#!/usr/bin/python3

from datetime import datetime
from datetime import timedelta
import requests, time
import configparser

# import the opencv module
import cv2

def get_datetime():
    return datetime.now()

def motion_trigger(m_state, current_timestamp): 
    # start_motion_addy = "http://10.10.0.14:5000/turn_all_off/" 
    # x = requests.get(start_motion_addy)
    if m_state: 
        print("Starting motion: {0}".format(current_timestamp))
    else: 
        print("Stopping motion: {0}".format(current_timestamp))

def main(): 
    # detection vars
    movement = False

    # load hanuted porch config
    config = configparser.ConfigParser() 
    config.read("../hp.cnf")
    # sample: config['zombie1_relay_one']['ip'])


    # datetime vars for motion detection
    motiontrue_timestamp = get_datetime()

    # capturing video 
    capture = cv2.VideoCapture(0)

    while capture.isOpened():
        # to read frame by frame
        _, img_1 = capture.read()
        _, img_2 = capture.read()

        # find difference between two frames 
        diff = cv2.absdiff(img_1, img_2)

        # to convert the frame to grayscale 
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) 
        
        # apply some blur to smoothen the frame 
        diff_blur = cv2.GaussianBlur(diff_gray, (5, 5), 0) 
        
        # to get the binary image 
        _, thresh_bin = cv2.threshold(diff_blur, 20, 255, cv2.THRESH_BINARY) 
        
        # to find contours 
        contours, hierarchy = cv2.findContours(thresh_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 

        # to draw the bounding box when the motion is detected 
        current_timestamp = get_datetime()
        prev_movement = movement
        for contour in contours: 
            x, y, w, h = cv2.boundingRect(contour) 
            if cv2.contourArea(contour) > 500: 
                cv2.rectangle(img_1, (x, y), (x+w, y+h), (0, 255, 0), 2)
                movement = True
                motiontrue_timestamp = current_timestamp

        # if not motion in specifiied interval toggle motion var
        if current_timestamp > motiontrue_timestamp + timedelta(seconds=60):
            movement = False

        # do something
        if not movement == prev_movement:
            if movement:
                # Starting motion
                motion_trigger(True, current_timestamp)
            else:
                # stopping motion
                motion_trigger(False, current_timestamp)


if __name__ == "__main__":
    main()
