#!/usr/bin/python3

# lidar_motion_detector_limited.py

import ydlidar
import time
import math

# --- Configuration ---
MOTION_THRESHOLD = 0.4      # meters (less sensitive)
ANGLE_TOLERANCE = 30.0      # degrees around rear-facing 180°
SCAN_INTERVAL = 0.1         # seconds
MOTION_HOLD_FRAMES = 5      # frames required to confirm motion
QUIET_FRAMES_REQUIRED = 5   # frames required to reset motion

# --- Helper Functions ---
def radians_to_degrees(rad):
    deg = math.degrees(rad)
    return (deg + 360) % 360  # Normalize to 0–360°

def is_in_rear_sector(angle_deg):
    return 150.0 <= angle_deg <= 210.0  # 180 ± 30°

# --- Motion Tracking ---
previous_ranges = {}
motion_frames = 0
quiet_frames = 0

def detect_motion(scan):
    global previous_ranges, motion_frames, quiet_frames
    current_ranges = {}
    motion_detected = False
    motion_angle = None

    for p in scan.points:
        angle_deg = round(radians_to_degrees(p.angle), 1)
        if not is_in_rear_sector(angle_deg):
            continue

        current_ranges[angle_deg] = p.range

        if angle_deg in previous_ranges:
            delta = abs(p.range - previous_ranges[angle_deg])
            if delta > MOTION_THRESHOLD:
                motion_detected = True
                motion_angle = angle_deg

    previous_ranges = current_ranges

    if motion_detected:
        motion_frames += 1
        quiet_frames = 0
    else:
        quiet_frames += 1
        if quiet_frames >= QUIET_FRAMES_REQUIRED:
            if motion_frames > 0:
                print("🔕 Motion lost")
            motion_frames = 0

    if motion_frames >= MOTION_HOLD_FRAMES:
        if motion_angle is not None:
            print(f"👀 Confirmed motion at ~{motion_angle:.1f}° (held {motion_frames} frames)")
        else:
            print(f"👀 Motion confirmed (held {motion_frames} frames), but no angle available this frame")
    else:
        print("…motion not yet confirmed")

# --- Initialize LIDAR ---
lidar = ydlidar.CYdLidar()
lidar.setlidaropt(ydlidar.LidarPropSerialPort, "/dev/ttyUSB0")  # Adjust if needed
#lidar.setlidaropt(ydlidar.LidarPropSerialBaudrate, 115200)
lidar.setlidaropt(ydlidar.LidarPropSerialBaudrate, 128000)
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
