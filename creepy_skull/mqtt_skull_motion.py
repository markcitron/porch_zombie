#!/usr/bin/python

import time
import paho.mqtt.client as mqtt
from robot_hat import Servo
import threading

# Lock to prevent overlapping motions
motion_lock = threading.Lock()

SERVO_8_INIT = -50
SERVO_7_INIT = -15
SERVO_8_ACTIVE = 30
SERVO_7_ACTIVE = 0
SERVO_8_SHAKE_LEFT = 35
SERVO_8_SHAKE_RIGHT = 25

servo_8 = Servo(8)
servo_7 = Servo(7)

# MQTT setup
MQTT_BROKER = "10.10.0.170"  # Change for production (currently my windows box)
# MQTT_BROKER = "10.10.0.175"  # Point to Mad Scientist
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
TRIGGER_KEYWORD = "creepy_skull"

# Helper for smooth movement
def smooth_move(servo, start, end, duration=2.0, steps=50):
    step_time = duration / steps
    delta = (end - start) / steps
    for i in range(steps):
        angle = start + delta * i
        servo.angle(angle)
        time.sleep(step_time)
    servo.angle(end)

def idle_position():
    servo_8.angle(SERVO_8_INIT)
    servo_7.angle(SERVO_7_INIT)

def active_motion():
    if not motion_lock.acquire(blocking=False):
        print("Motion already active, ignoring trigger.")
        return
    try:
        # Move to active position slowly and smoothly
        smooth_move(servo_8, SERVO_8_INIT, SERVO_8_ACTIVE, duration=3.0)
        smooth_move(servo_7, SERVO_7_INIT, SERVO_7_ACTIVE, duration=3.0)
        time.sleep(1.5)  # brief pause

        # Slowly shake head between 35 and 25 for 5 cycles
        for _ in range(5):
            smooth_move(servo_8, SERVO_8_ACTIVE, SERVO_8_SHAKE_LEFT, duration=1.0)
            time.sleep(0.5)
            smooth_move(servo_8, SERVO_8_SHAKE_LEFT, SERVO_8_SHAKE_RIGHT, duration=1.0)
            time.sleep(0.5)
            smooth_move(servo_8, SERVO_8_SHAKE_RIGHT, SERVO_8_ACTIVE, duration=1.0)
            time.sleep(0.5)

        time.sleep(20)  # 20 second pause

        # Return to idle slowly
        smooth_move(servo_8, SERVO_8_ACTIVE, SERVO_8_INIT, duration=3.0)
        smooth_move(servo_7, SERVO_7_ACTIVE, SERVO_7_INIT, duration=3.0)
    finally:
        motion_lock.release()

# MQTT callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received MQTT: {payload}")
    if payload == TRIGGER_KEYWORD:
        active_motion()

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_message = on_message

# Add disconnect handler for auto-reconnect
def on_disconnect(client, userdata, rc):
    print(f"MQTT disconnected with code {rc}. Attempting reconnect...")
    while rc != 0:
        try:
            rc = client.reconnect()
            if rc == 0:
                print("MQTT reconnected successfully.")
        except Exception as e:
            print(f"Reconnect failed: {e}")
        time.sleep(5)
client.on_disconnect = on_disconnect

client.connect(MQTT_BROKER, MQTT_PORT, keepalive=120)
client.subscribe(MQTT_TOPIC)

print("Creepy Skull MQTT motion listener active. Waiting for trigger...")
idle_position()
client.loop_forever()
