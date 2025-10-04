#!/usr/bin/python

import time
import paho.mqtt.client as mqtt
from robot_hat import Servo
import threading

# Lock to prevent overlapping motions
motion_lock = threading.Lock()

# Servo setup
SERVO_8_INIT = -50
SERVO_7_INIT = -10
SERVO_8_ACTIVE = 45
SERVO_7_ACTIVE = -10
SERVO_8_MIN = -50
SERVO_8_MAX = 45
SERVO_7_MIN = -10
SERVO_7_MAX = 45

servo_8 = Servo(8)
servo_7 = Servo(7)

# MQTT setup
MQTT_BROKER = "10.10.0.170"  # Change for production (currently my windows box)
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
        # Move to active position
        smooth_move(servo_8, SERVO_8_INIT, SERVO_8_ACTIVE, duration=2.0)
        servo_7.angle(SERVO_7_ACTIVE)
        # 30 seconds of smooth random motion
        start_time = time.time()
        while time.time() - start_time < 30:
            # Move up/down and left/right smoothly
            for angle8 in range(SERVO_8_ACTIVE, SERVO_8_MAX, 2):
                servo_8.angle(angle8)
                time.sleep(0.05)
            for angle8 in range(SERVO_8_MAX, SERVO_8_ACTIVE, -2):
                servo_8.angle(angle8)
                time.sleep(0.05)
            for angle7 in range(SERVO_7_ACTIVE, SERVO_7_MAX, 2):
                servo_7.angle(angle7)
                time.sleep(0.05)
            for angle7 in range(SERVO_7_MAX, SERVO_7_ACTIVE, -2):
                servo_7.angle(angle7)
                time.sleep(0.05)
        # Return to idle
        smooth_move(servo_8, SERVO_8_ACTIVE, SERVO_8_INIT, duration=2.0)
        smooth_move(servo_7, SERVO_7_ACTIVE, SERVO_7_INIT, duration=2.0)
    finally:
        motion_lock.release()

# MQTT callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received MQTT: {payload}")
    if payload == TRIGGER_KEYWORD:
        threading.Thread(target=active_motion).start()

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(MQTT_TOPIC)

print("Creepy Skull MQTT motion listener active. Waiting for trigger...")
idle_position()
client.loop_forever()
