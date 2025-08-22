#!/usr/bin/python3

import time
import ydlidar

from movement_detector import MovementDetector
from servo_controller import ServoController
from mode_manager import ModeManager
from lidar_utils import find_nearest_target_angle

# --- Initialize LIDAR ---
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

print("🎃 Scarecrow system online...")

# --- Initialize Modules ---
scan = ydlidar.LaserScan()
detector = MovementDetector(threshold=120, min_points=8)
servo = ServoController()
mode_manager = ModeManager()

try:
    while True:
        if lidar.doProcessSimple(scan):
            # Convert scan.points to list of (angle_rad, distance_mm)
            scan_data = [(p.angle, p.range * 1000) for p in scan.points if p.range > 0]

            movement = detector.detect_movement([d for _, d in scan_data])
            mode_manager.update_mode(movement)

            if mode_manager.get_mode() == "patrol":
                servo.patrol_motion()
            else:
                pan_angle = find_nearest_target_angle(scan_data)
                servo.snap_to_target(pan_angle)

        time.sleep(0.05)

except KeyboardInterrupt:
    print("🛑 Shutting down...")

finally:
    lidar.turnOff()
    lidar.disconnecting()
    servo.reset_position()
