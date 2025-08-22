#!/usr/bin/python3

# lidar_utils.py

import math

def find_nearest_target_angle(scan):
    front_zone = [pt for pt in scan if 2.0 <= pt[0] <= 4.0 and pt[1] > 0]
    if not front_zone:
        return 0

    nearest = min(front_zone, key=lambda x: x[1])
    angle_rad = nearest[0]
    normalized = (angle_rad - 2.0) / (4.0 - 2.0)
    pan_angle = 45 - (normalized * 90)
    return int(pan_angle)
