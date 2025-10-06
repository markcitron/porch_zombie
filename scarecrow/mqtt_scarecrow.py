#!/usr/bin/python

import time
import paho.mqtt.client as mqtt
import threading
import lib8relind

# Lock to prevent overlapping motions
motion_lock = threading.Lock()

# MQTT setup
MQTT_BROKER = "10.10.0.170"  # Change for production
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
TRIGGER_KEYWORD = "scarecrow"

# Placeholder functions for linear actuators
def idle_position():
	# Set both actuators to idle position
	print("Setting actuators to idle position.")
	# actuator_1_idle()
	# actuator_2_idle()

def activate_actuator_1():
	print("Activating actuator 1!")
	# TODO: Add code to trigger actuator 1

def activate_actuator_2():
	print("Activating actuator 2!")
	# TODO: Add code to trigger actuator 2

def active_motion():
	if not motion_lock.acquire(blocking=False):
		print("Motion already active, ignoring trigger.")
		return
	try:
		# Example sequence: activate both actuators
		activate_actuator_1()
		time.sleep(1)
		activate_actuator_2()
		time.sleep(1)
		# Hold active for demonstration
		time.sleep(5)
		idle_position()
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

print("Scarecrow MQTT motion listener active. Waiting for trigger...")
idle_position()
client.loop_forever()
