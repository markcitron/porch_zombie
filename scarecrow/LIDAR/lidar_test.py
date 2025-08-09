#!/usr/bin/env python3

import time
from ydlidar import YDLidarX4

# Set your serial port and baud rate
PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

def run():
    lidar = YDLidarX4(port=PORT, baudrate=BAUDRATE)
    
    if not lidar.connect():
        print("❌ Failed to connect to YDLidar X4.")
        return

    print("✅ Connected to YDLidar X4.")
    
    lidar.start_scan()
    print("🔄 Scanning... Press Ctrl+C to stop.")

    try:
        while True:
            scan = lidar.get_scan()
            if scan:
                print("Scan:")
                for point in scan:
                    angle = point.angle
                    distance = point.distance
                    print(f"  Angle: {angle:.2f}°, Distance: {distance:.2f} mm")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("🛑 Stopping scan...")
    finally:
        lidar.stop()
        lidar.disconnect()
        print("✅ LIDAR disconnected.")

if __name__ == "__main__":
    run()
