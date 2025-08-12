#!/usr/bin/python3

from ydlidar import CYdLidar, LaserScan
import ydlidar
import time

lidar = CYdLidar()
lidar.setlidaropt(ydlidar.LidarPropSerialPort, "/dev/ttyUSB0")
lidar.setlidaropt(ydlidar.LidarPropSerialBaudrate, 230400)  # Try 230400
lidar.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
lidar.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TOF)
lidar.setlidaropt(ydlidar.LidarPropIntenstiy, True)

if not lidar.initialize() or not lidar.turnOn():
    print("❌ LIDAR failed to start")
    exit(1)

scan = LaserScan()

try:
    while True:
        if lidar.doProcessSimple(scan):
            print(f"Scan received: {len(scan.points)} points")
        time.sleep(0.1)

except KeyboardInterrupt:
    lidar.turnOff()
    lidar.disconnecting()
