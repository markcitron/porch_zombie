#!/usr/bin/python3

import ydlidar
import time
import matplotlib.pyplot as plt
import numpy as np

# --- Configuration ---
TARGET_ANGLE = 4.0
ANGLE_TOLERANCE = 1.0

# --- Helper Functions ---
def get_distance_at_angle(scan, target_angle, tolerance=1.0):
    points = [p for p in scan.points if target_angle - tolerance <= p.angle <= target_angle + tolerance]
    if points:
        return sum(p.range for p in points) / len(points)
    return None

def print_scan_diagnostics(scan, target_angle):
    if not scan.points:
        print("No scan points received.")
        return

    # Print first 10 points
    print("\nSample scan points:")
    for i, p in enumerate(scan.points[:10]):
        print(f"{i+1:02d}) Angle: {p.angle:.2f}°, Range: {p.range:.2f}m")

    # Print angle range
    angles = [p.angle for p in scan.points]
    print(f"\nAngle range: {min(angles):.2f}° to {max(angles):.2f}°")

    # Closest point to target angle
    closest = min(scan.points, key=lambda p: abs(p.angle - target_angle))
    print(f"Closest to {target_angle}° → Angle: {closest.angle:.2f}°, Range: {closest.range:.2f}m")

def plot_scan(scan):
    angles = np.array([np.deg2rad(p.angle) for p in scan.points])
    ranges = np.array([p.range for p in scan.points])

    plt.figure(figsize=(6,6))
    ax = plt.subplot(111, polar=True)
    ax.scatter(angles, ranges, s=5, c='blue', alpha=0.6)

    # Highlight target angle
    target_rad = np.deg2rad(TARGET_ANGLE)
    ax.plot([target_rad, target_rad], [0, max(ranges)], color='red', linewidth=1.5, label=f"{TARGET_ANGLE}°")

    ax.set_theta_zero_location('N')  # Adjust based on your mounting
    ax.set_theta_direction(-1)       # Clockwise
    plt.title("YDLIDAR G4 Scan")
    plt.legend()
    plt.show()

# --- Initialize LIDAR ---
lidar = ydlidar.CYdLidar()
lidar.setlidaropt(ydlidar.LidarPropSerialPort, "/dev/ttyUSB0")
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
                print(f"\nDistance at {TARGET_ANGLE}°: {distance:.2f} meters")
            else:
                print(f"\nNo data near {TARGET_ANGLE}°")

            print_scan_diagnostics(scan, TARGET_ANGLE)
            plot_scan(scan)
            break  # Just one scan for testing

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopping LIDAR...")

finally:
    lidar.turnOff()
    lidar.disconnecting()
