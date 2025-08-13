#!/usr/bin/python3

import ydlidar
import time
import random
from robot_hat import Servo

# Servo Setup
pan_servo = Servo(8)   # Pan: left/right
tilt_servo = Servo(7)  # Tilt: up/down

PAN_MIN = -90
PAN_MAX = 90
TILT_MIN = -45
TILT_MAX = 45

# Smoothing Variables
current_pan = 0
current_tilt = 0

# Patrol Mode
patrol_angle = PAN_MIN
patrol_direction = 1
motion_timeout = 3
last_motion_time = time.time()

# Mapping and Easing
def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def ease_angle(current, target, factor):
    return current + factor * (target - current)

# LIDAR Setup
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

print("LIDAR active. Monitoring front distance...")

scan = ydlidar.LaserScan()

try:
    while True:
        if lidar.doProcessSimple(scan):
            front_points = [p for p in scan.points if -1.0 <= p.angle <= 1.0]
            if front_points:
                avg_distance = sum(p.range for p in front_points) / len(front_points)

                # Target detected within 2.5 meters
                if avg_distance < 2.5:
                    last_motion_time = time.time()

                    # Map distance to pan angle (closer = more aggressive turn)
                    target_pan = map_range(avg_distance, 0.3, 2.5, 0, -60)
                    target_tilt = map_range(avg_distance, 0.3, 2.5, 20, 0)

                    current_pan = ease_angle(current_pan, target_pan, factor=0.1)
                    current_tilt = ease_angle(current_tilt, target_tilt, factor=0.1)

                    pan_servo.angle(current_pan)
                    tilt_servo.angle(current_tilt)

                    print(f"👀 Target at {avg_distance:.2f}m → Pan: {current_pan:.1f}, Tilt: {current_tilt:.1f}")
                else:
                    # Idle Patrol Mode
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

                        print(f"🕵️ Patrolling → Pan: {patrol_angle}")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping LIDAR and servos...")

finally:
    lidar.turnOff()
    lidar.disconnecting()
