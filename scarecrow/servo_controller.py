#!/usr/bin/python3 

import time
from robot_hat import Servo

class ServoController:
    def __init__(self):
        # Initialize servos on correct pins
        self.pan = Servo(7)   # Pan: left/right
        self.tilt = Servo(8)  # Tilt: up/down

        # Define safe operating ranges
        self.pan_min = -45
        self.pan_max = 45
        self.tilt_min = -25
        self.tilt_max = 25

    def patrol_motion(self):
        """Slow sweep from right to left and back"""
        for angle in range(self.pan_min, self.pan_max + 1, 3):
            self.pan.angle(angle)
            self.tilt.angle(0)  # Neutral tilt
            time.sleep(0.05)
        for angle in range(self.pan_max, self.pan_min - 1, -3):
            self.pan.angle(angle)
            self.tilt.angle(0)
            time.sleep(0.05)

    def snap_to_target(self, pan_angle):
        """Snap head to target angle with slight upward tilt"""
        pan_angle = max(self.pan_min, min(self.pan_max, pan_angle))
        self.pan.angle(pan_angle)
        self.tilt.angle(-10)  # Dramatic upward lean
        time.sleep(0.1)

    def reset_position(self):
        """Return head to neutral position"""
        self.pan.angle(0)
        self.tilt.angle(0)
