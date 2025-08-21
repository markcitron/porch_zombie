#!/usr/bin/python3

# scarecrow_tracker.py

import ydlidar
import time
import math
import random
from robot_hat import Servo

# --- Configuration ---
PAN_MIN = -90   # Rightmost (from LIDAR's POV)
PAN_MAX = 90    # Leftmost
TILT_MIN = -14  # Up
TILT_MAX = 45   # Down
PAN_STEP = 5    # Degrees per sweep step
SCAN_INTERVAL = 0.1  # Seconds between scans
TRACK_HOLD_TIME = 2.0  # Seconds to hold tracking position
ANGLE_TOLERANCE = 0.2  # Radians ± around target

# --- Servo Setup ---
pan_servo = Servo("P0")   # Adjust pin as needed
tilt_servo = Servo("P1")  # Adjust pin as needed

def set_pan(angle_deg):
    # Positive = left, Negative = right
    angle_deg = max(PAN_MIN, min(PAN_MAX, angle_deg))
    pan_servo.angle(angle_deg)

def set_tilt(angle_deg):
    # Negative = up, Positive = down
    angle_deg = max(TILT_MIN, min(TILT_MAX, angle_deg))
    tilt_servo.angle(angle_deg)

def compute_tilt_from_distance(distance):
    # Map 0.2m (close) → TILT_MAX (down), 3.0m (far) → TILT_MIN (up)
    distance = max(0.2, min(distance, 3.0))
    ratio = (distance - 0.2) / (3.0 - 0.2)
    return TILT_MAX - ratio * (TILT_MAX - TILT_MIN)

# --- LIDAR Setup ---
lidar = ydlidar.CYdLidar()
lidar.setlidaropt(ydlidar.LidarPropSerialPort, "/dev/ttyUSB0")
lidar.setlidaropt(ydlidar.LidarPropSerialBaudrate, 115200)
lidar.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
lidar.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
lidar.setlidaropt(ydlidar.LidarPropIntenstiy, True)

if not lidar.initialize():
    print("❌ Failed to initialize LIDAR")
    exit(1)

if not lidar.turnOn():
    print("❌ Failed to start LIDAR scanning")
    exit(1)

scan = ydlidar.LaserScan()

# --- Helper Functions ---
def get_distance_at_angle(scan, target_angle_rad, tolerance=ANGLE_TOLERANCE):
    points = [p for p in scan.points if target_angle_rad - tolerance <= p.angle <= target_angle_rad + tolerance]
    if points:
        return sum(p.range for p in points) / len(points)
    return None

def deg_to_rad(deg):
    return deg * math.pi / 180.0

# --- Main Loop ---
try:
    print("🧟 Scarecrow tracking system active...")
    sweeping_forward = True
    pan_angle = PAN_MIN

    while True:
        set_pan(pan_angle)
        set_tilt(0)  # Neutral tilt

        if lidar.doProcessSimple(scan):
            target_rad = deg_to_rad(pan_angle)
            distance = get_distance_at_angle(scan, target_rad)

            if distance and 0.2 < distance < 3.0:
                print(f"🎯 Motion detected at {pan_angle}°, {distance:.2f}m")
                set_pan(pan_angle)
                tilt_angle = compute_tilt_from_distance(distance)
                set_tilt(tilt_angle)
                time.sleep(TRACK_HOLD_TIME)
            else:
                print(f"🔍 Scanning at {pan_angle}°... No motion")

        # Sweep logic
        if sweeping_forward:
            pan_angle += PAN_STEP
            if pan_angle >= PAN_MAX:
                sweeping_forward = False
        else:
            pan_angle -= PAN_STEP
            if pan_angle <= PAN_MIN:
                sweeping_forward = True

        # Add jitter for lifelike movement
        time.sleep(SCAN_INTERVAL + random.uniform(-0.05, 0.1))

except KeyboardInterrupt:
    print("🛑 Shutting down scarecrow...")

finally:
    lidar.turnOff()
    lidar.disconnecting()
    pan_servo.release()
    tilt_servo.release()
