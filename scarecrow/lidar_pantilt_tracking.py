#!/usr/bin/python3

import time
import random
from robot_hat import Servo
from ydlidar import CYdLidar, LaserScan  
import ydlidar

# 🛠️ Servo Setup
pan_servo = Servo(8)   # Pan: left/right
tilt_servo = Servo(7)  # Tilt: up/down

# 🎚️ Servo Angle Limits
PAN_MIN = -90
PAN_MAX = 90
TILT_MIN = -45
TILT_MAX = 45

# 🧭 LIDAR Tracking Zone
FRONT_ARC_MIN = 120
FRONT_ARC_MAX = 240
MIN_RANGE = 0.1  # meters

# 🎛️ Smoothing Variables
current_pan = 0
current_tilt = 0

# 👁️ Patrol Mode Variables
patrol_angle = PAN_MIN
patrol_direction = 1
motion_timeout = 3
last_motion_time = time.time()

# 🔧 Mapping and Easing
def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def ease_angle(current, target, factor):
    return current + factor * (target - current)

# 🧠 LIDAR Setup
lidar = CYdLidar()
lidar.setlidaropt(ydlidar.LidarPropSerialPort, "/dev/ttyUSB0")
lidar.setlidaropt(ydlidar.LidarPropSerialBaudrate, 115200)
lidar.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
lidar.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TOF)
lidar.setlidaropt(ydlidar.LidarPropIntenstiy, True)

if not lidar.initialize() or not lidar.turnOn():
    print("❌ LIDAR failed to start")
    exit(1)

print("✅ LIDAR tracking active...")

scan = LaserScan()

try:
    while True:
        if lidar.doProcessSimple(scan):
            points = scan.points

            # 🧪 Debug: Confirm point structure
            if points:
                print(f"First point: {points[0]}")
                print(f"Attributes: {dir(points[0])}")
                # You can comment out these lines once confirmed

            # Filter points in front arc
            front_points = [
                p for p in points
                if hasattr(p, 'angle') and hasattr(p, 'range')
                and FRONT_ARC_MIN <= p.angle <= FRONT_ARC_MAX
                and p.range > MIN_RANGE
            ]

            if front_points:
                last_motion_time = time.time()

                # Find closest point
                target = min(front_points, key=lambda p: p.range)
                lidar_angle = target.angle
                lidar_range = target.range

                # Map LIDAR angle to pan servo
                target_pan = map_range(lidar_angle, FRONT_ARC_MIN, FRONT_ARC_MAX, PAN_MAX, PAN_MIN)

                # Optional: Map range to tilt (closer = tilt down)
                target_tilt = map_range(lidar_range, 0.2, 2.0, TILT_MAX, TILT_MIN)

                current_pan = ease_angle(current_pan, target_pan, factor=0.1)
                current_tilt = ease_angle(current_tilt, target_tilt, factor=0.1)

                pan_servo.angle(current_pan)
                tilt_servo.angle(current_tilt)

                print(f"🎯 Tracking object at {lidar_angle:.1f}°, {lidar_range:.2f}m → pan {current_pan:.1f}, tilt {current_tilt:.1f}")

            else:
                # 💤 Patrol Mode
                idle_duration = time.time() - last_motion_time
                if idle_duration > motion_timeout:
                    patrol_step = 1 if idle_duration > 10 else 3

                    if random.random() < 0.02:
                        time.sleep(random.uniform(0.5, 1.5))

                    patrol_angle += patrol_direction * patrol_step
                    if patrol_angle >= PAN_MAX or patrol_angle <= PAN_MIN:
                        patrol_direction *= -1
                        patrol_angle = max(min(patrol_angle, PAN_MAX), PAN_MIN)

                    pan_servo.angle(patrol_angle)
                    tilt_servo.angle(0)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("🛑 Stopping tracker...")

finally:
    lidar.turnOff()
    lidar.disconnecting()
