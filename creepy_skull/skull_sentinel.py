#!/usr/bin/python3

# lidar_motion_detector_limited.py

import ydlidar
import time
import math

# --- Configuration ---
MOTION_THRESHOLD = 0.4      # meters (less sensitive)
ANGLE_TOLERANCE = 30.0      # degrees around rear-facing 180°
SCAN_INTERVAL = 0.1         # seconds

# --- Helper Functions ---
def radians_to_degrees(rad):
    deg = math.degrees(rad)
    return (deg + 360) % 360  # Normalize to 0–360°

def is_in_rear_sector(angle_deg):
    return 150.0 <= angle_deg <= 210.0  # 180 ± 30°

previous_ranges = {}

def detect_motion(scan):
    global previous_ranges
    current_ranges = {}

    for p in scan.points:
        angle_deg = round(radians_to_degrees(p.angle), 1)
        if not is_in_rear_sector(angle_deg):
            continue  # Skip angles outside rear-facing sector

        current_ranges[angle_deg] = p.range

        if angle_deg in previous_ranges:
            delta = abs(p.range - previous_ranges[angle_deg])
            if delta > MOTION_THRESHOLD:
                print(f"👀 Motion detected at {angle_deg:.1f}° (Δ {delta:.2f} m)")

    previous_ranges = current_ranges

# --- Initialize LIDAR ---
lidar = ydlidar.CYdLidar()
lidar.setlidaropt(ydlidar.LidarPropSerialPort, "/dev/ttyUSB0")  # Adjust if needed
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

print("🌀 LIDAR scanning... Watching for motion in rear sector (150°–210°)")

scan = ydlidar.LaserScan()

# --- Main Loop ---
try:
    while True:
        if lidar.doProcessSimple(scan):
            detect_motion(scan)
        time.sleep(SCAN_INTERVAL)

except KeyboardInterrupt:
    print("🛑 Stopping LIDAR...")

finally:
    lidar.turnOff()
    lidar.disconnecting()
