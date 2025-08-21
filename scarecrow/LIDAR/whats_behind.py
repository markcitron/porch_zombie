#!/usr/bin/python3

import ydlidar
import time

# Create and configure the LIDAR
lidar = ydlidar.CYdLidar()
lidar.setlidaropt(ydlidar.LidarPropSerialPort, "/dev/ttyUSB0")  # Update if needed
lidar.setlidaropt(ydlidar.LidarPropSerialBaudrate, 115200)
lidar.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
lidar.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
lidar.setlidaropt(ydlidar.LidarPropIntenstiy, True)

# Initialize and start
if not lidar.initialize():
    print("Failed to initialize LIDAR")
    exit(1)

if not lidar.turnOn():
    print("Failed to start LIDAR scanning")
    exit(1)

print("LIDAR scanning... Showing distance at angle ≈ 0°")

scan = ydlidar.LaserScan()

try:
    while True:
        if lidar.doProcessSimple(scan):
            # Filter for angle near 0° (±1° tolerance)
            front_points = [p for p in scan.points if -1.0 <= p.angle <= 1.0]
            if front_points:
                # Average the distances for stability
                avg_distance = sum(p.range for p in front_points) / len(front_points)
                print(f"Distance at 0°: {avg_distance:.2f} meters")
            else:
                print("No data near 0°")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping LIDAR...")

finally:
    lidar.turnOff()
    lidar.disconnecting()
