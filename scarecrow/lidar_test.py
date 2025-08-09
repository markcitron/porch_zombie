#!/usr/bin/python3

from rplidar import RPLidar

PORT_NAME = '/dev/ttyUSB0'

def run():
    lidar = RPLidar(PORT_NAME)
    try:
        print("Starting LIDAR scan...")
        for scan in lidar.iter_scans():
            print('Scan:')
            for (_, angle, distance) in scan:
                print(f'Angle: {angle:.2f}°, Distance: {distance:.2f} mm')
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        lidar.stop()
        lidar.disconnect()

if __name__ == '__main__':
    run()
