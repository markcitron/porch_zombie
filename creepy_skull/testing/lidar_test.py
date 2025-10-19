#!/usr/bin/python3

# lidar_test.py
from ydlidar import YDlidar
import time

def main():
    lidar = YDlidar()
    lidar.setlidaropt(lidar.LidarOpt.SerialPort, "/dev/ttyUSB0")
    lidar.setlidaropt(lidar.LidarOpt.SerialBaudrate, 115200)
    lidar.setlidaropt(lidar.LidarOpt.DeviceType, lidar.DeviceType.Serial)
    lidar.setlidaropt(lidar.LidarOpt.LidarType, lidar.LidarType.Triangle)
    lidar.setlidaropt(lidar.LidarOpt.ScanFrequency, 10.0)

    if not lidar.initialize():
        print("❌ Initialization failed")
        return

    if not lidar.turn_on():
        print("❌ Failed to start LIDAR")
        return

    print("🚀 Scanning...")
    try:
        for i in range(100):
            scan = lidar.do_process_simple()
            if scan:
                print(f"Scan #{i}: {len(scan)} points")
                for point in scan[:5]:
                    print(f"  Angle: {point.angle:.2f}°, Distance: {point.range:.2f}mm")
            else:
                print("⚠️ No scan data")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("🛑 Interrupted")
    finally:
        lidar.turn_off()
        lidar.disconnect()
        print("🔌 LIDAR disconnected")

if __name__ == "__main__":
    main()
