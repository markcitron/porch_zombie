#!/usr/bin/python3

#!/usr/bin/python3

import ydlidar
import time
import random
from robot_hat import Servo

# === Servo Setup ===
pan_servo = Servo(8)   # Pan: left/right
tilt_servo = Servo(7)  # Tilt: up/down

# === Servo Angle Limits ===
PAN_MIN = -90
PAN_MAX = 90
TILT_MIN = -45
TILT_MAX = 45

# === LIDAR Setup ===
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
TRACKING_ARC = 45.0  # degrees
MIN_RANGE = 0.3      # meters
MAX_RANGE = 3.0      # meters
PATROL_INTERVAL = 2.0  # seconds

# === Motion State ===
MODE_PATROL = "patrol"
MODE_TRACK = "track"
mode = MODE_PATROL
last_patrol = time.time()
last_motion_time = time.time()
motion_timeout = 3

# === Smoothing Variables ===
current_pan = 0
current_tilt = 0

# === Patrol Variables ===
patrol_angle = PAN_MIN
patrol_direction = 1

# === LIDAR Initialization ===
lidar = ydlidar.CYdLidar()
lidar.setlidaropt(ydlidar.LidarPropSerialPort, SERIAL_PORT)
lidar.setlidaropt(ydlidar.LidarPropSerialBaudrate, BAUDRATE)
lidar.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
lidar.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
lidar.setlidaropt(ydlidar.LidarPropIntenstiy, True)
lidar.setLidarModel(G4)

if not lidar.initialize():
    print("Failed to initialize LIDAR")
    exit(1)

if not lidar.turnOn():
    print("Failed to start LIDAR scanning")
    exit(1)

print("Scarecrow is online. Patrolling...")

scan = ydlidar.LaserScan()

# === Utility Functions ===
def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def ease_angle(current, target, factor):
    return current + factor * (target - current)

def angle_to_servo(angle):
    # Map -90 to +90 → PAN_MIN to PAN_MAX
    return int(map_range(angle, -90, 90, PAN_MIN, PAN_MAX))

def estimate_tilt(distance):
    # Map distance to tilt angle
    return int(map_range(distance, MIN_RANGE, MAX_RANGE, TILT_MAX, TILT_MIN))

def detect_target(scan):
    points = [p for p in scan.points if abs(p.angle) <= TRACKING_ARC and MIN_RANGE <= p.range <= MAX_RANGE]
    return min(points, key=lambda p: p.range) if points else None

# === Main Loop ===
try:
    while True:
        if lidar.doProcessSimple(scan):
            target = detect_target(scan)
            if target:
                last_motion_time = time.time()
                if mode != MODE_TRACK:
                    print("Target detected! Switching to tracking mode.")
                mode = MODE_TRACK

                target_pan = angle_to_servo(target.angle)
                target_tilt = estimate_tilt(target.range)

                current_pan = ease_angle(current_pan, target_pan, factor=0.1)
                current_tilt = ease_angle(current_tilt, target_tilt, factor=0.1)

                pan_servo.angle(current_pan)
                tilt_servo.angle(current_tilt)

                print(f"Tracking → Angle: {target.angle:.1f}°, Range: {target.range:.2f}m")
            else:
                idle_duration = time.time() - last_motion_time
                if idle_duration > motion_timeout:
                    if mode == MODE_TRACK:
                        print("Target lost. Returning to patrol.")
                        mode = MODE_PATROL

        if mode == MODE_PATROL and time.time() - last_patrol > PATROL_INTERVAL:
            patrol_step = 1 if time.time() - last_motion_time > 10 else 3

            if random.random() < 0.02:
                time.sleep(random.uniform(0.5, 1.5))

            patrol_angle += patrol_direction * patrol_step
            if patrol_angle >= PAN_MAX or patrol_angle <= PAN_MIN:
                patrol_direction *= -1
                patrol_angle = max(min(patrol_angle, PAN_MAX), PAN_MIN)

            pan_servo.angle(patrol_angle)
            tilt_servo.angle(0)
            last_patrol = time.time()
            print("Patrolling...")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Shutting down scarecrow...")

finally:
    lidar.turnOff()
    lidar.disconnecting()
