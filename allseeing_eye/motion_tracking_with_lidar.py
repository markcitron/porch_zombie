#!/usr/bin/python

from rplidar import RPLidar
import time
import paho.mqtt.client as mqtt

PORT_NAME = '/dev/ttyUSB0'
DISTANCE_THRESHOLD = 100  # mm
SCAN_INTERVAL = 0.2

ZONES = {
    'front': (315, 45),
    'left': (45, 135),
    'rear': (135, 225),
    'right': (225, 315)
}

MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'lidar/motion'

lidar = RPLidar(PORT_NAME)
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

def get_scan_snapshot():
    snapshot = {}
    for scan in lidar.iter_measurments(max_buf_meas=500):
        quality, angle, distance = scan[1], int(scan[2]), scan[3]
        if quality > 0:
            snapshot[angle] = distance
        if len(snapshot) >= 360:
            break
    return snapshot

def angle_in_zone(angle, zone_range):
    start, end = zone_range
    if start < end:
        return start <= angle < end
    else:
        return angle >= start or angle < end  # Wrap-around

def detect_motion_by_zone(prev, curr):
    events = []
    for angle in range(360):
        d1 = prev.get(angle, 0)
        d2 = curr.get(angle, 0)
        if d1 > 0 and d2 > 0 and abs(d1 - d2) > DISTANCE_THRESHOLD:
            for zone_name, zone_range in ZONES.items():
                if angle_in_zone(angle, zone_range):
                    event = {
                        'zone': zone_name,
                        'angle': angle,
                        'distance': d2,
                        'delta': abs(d1 - d2)
                    }
                    events.append(event)
                    break
    return events

def publish_event(event):
    mqtt_client.publish(MQTT_TOPIC, str(event))
    print(f"📤 Published: {event}")

try:
    print("Starting LIDAR...")
    lidar.start_motor()
    time.sleep(2)

    prev_scan = get_scan_snapshot()
    while True:
        time.sleep(SCAN_INTERVAL)
        curr_scan = get_scan_snapshot()
        events = detect_motion_by_zone(prev_scan, curr_scan)
        for event in events:
            publish_event(event)
        prev_scan = curr_scan

except KeyboardInterrupt:
    print("Stopping...")
finally:
    lidar.stop()
    lidar.disconnect()
    mqtt_client.disconnect()
