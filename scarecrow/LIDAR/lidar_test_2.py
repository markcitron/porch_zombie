#!/usr/bin/python3

import ydlidar
import time

# Create and configure the LIDAR
lidar = ydlidar.CYdLidar()

# Required settings
lidar.setlidaropt(ydlidar.LidarPropSerialPort, "/dev/ttyUSB0")  # Adjust as needed
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

print("LIDAR scanning... Press Ctrl+C to stop.")

# Create an empty LaserScan object to hold results
scan = ydlidar.LaserScan()

try:
    while True:
        if lidar.doProcessSimple(scan):
            print(f"Scan received: {len(scan.points)} points")
            for point in scan.points:
                print(f"Angle: {point.angle:.2f}°, Distance: {point.range:.2f}m, Intensity: {point.intensity}")
        else:
            print("No scan data received.")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping LIDAR...")

finally:
    lidar.turnOff()
    lidar.disconnecting()
