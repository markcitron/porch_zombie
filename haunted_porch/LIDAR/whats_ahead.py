#!/usr/bin/python3

# whats_ahead.py

import ydlidar
import time

# --- Configuration ---
# TARGET_ANGLE = -180.0  # Rear-facing direction
TARGET_ANGLE = 3.14  # Rear-facing direction
ANGLE_TOLERANCE = 0.2  # Radians ± around target

# --- Helper Function ---
def get_distance_at_angle(scan, target_angle, tolerance=1.0):
    points = [p for p in scan.points if target_angle - tolerance <= p.angle <= target_angle + tolerance]
    if points:
        return sum(p.range for p in points) / len(points)
    return None

# --- Initialize LIDAR ---
lidar = ydlidar.CYdLidar()
lidar.setlidaropt(ydlidar.LidarPropSerialPort, "/dev/ttyUSB0")  # Adjust if needed
lidar.setlidaropt(ydlidar.LidarPropSerialBaudrate, 115200)
lidar.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
lidar.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
lidar.setlidaropt(ydlidar.LidarPropIntenstiy, True)

if not lidar.initialize():
    print("Failed to initialize LIDAR")
    exit(1)

if not lidar.turnOn():
    print("Failed to start LIDAR scanning")
    exit(1)

print(f"LIDAR scanning... Showing distance at angle ≈ {TARGET_ANGLE}°")

scan = ydlidar.LaserScan()

try:
    while True:
        if lidar.doProcessSimple(scan):
            distance = get_distance_at_angle(scan, TARGET_ANGLE, ANGLE_TOLERANCE)
            if distance is not None:
                print(f"Distance at {TARGET_ANGLE}°: {distance:.2f} meters")
            else:
                print(f"No data near {TARGET_ANGLE}°")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping LIDAR...")

finally:
    lidar.turnOff()
    lidar.disconnecting()
