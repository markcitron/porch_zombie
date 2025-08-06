#!/usr/bin/python3

from config import *

def map_range(value, input_min, input_max, output_min, output_max):
    value = max(min(value, input_max), input_min)  # Clamp
    return output_min + (float(value - input_min) / (input_max - input_min)) * (output_max - output_min)

def get_servo_angles(x, y):
    pan = map_range(x, 0, FRAME_WIDTH, PAN_MIN, PAN_MAX)
    tilt = map_range(y, 0, FRAME_HEIGHT, TILT_MAX, TILT_MIN)  # Inverted tilt
    return int(pan), int(tilt)
