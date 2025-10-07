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

# set up linear actuator relays
relay1 = LinAct("", 1)
relay2 = LinAct("", 2)
relay3 = LinAct("", 3)
relay4 = LinAct("", 4)
relay5 = LinAct("", 5)
relay6 = LinAct("", 6)
relay7 = LinAct("", 7)
relay8 = LinAct("", 8)

# Placeholder functions for linear actuators
def idle_position():
	# Set both actuators to idle position
	print("Setting actuators to idle position.")
	relay1.extend()
	time.sleep(.1)
	relay6.extent()
	return True

def someone_is_here():
	print("Someone is here!")
	relay6.contact()
	time.sleep(15)
	relay1.contract()
	return True

def active_motion():
	if not motion_lock.acquire(blocking=False):
		print("Motion already active, ignoring trigger.")
		return
	try:
		someone_is_here()
		time.sleep(30)
		idle_position()
	finally:
		motion_lock.release()

# MQTT callback
def on_message(client, userdata, msg):
	payload = msg.payload.decode()
	print("Received MQTT: {}".format(payload))
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
			print("Reconnect failed: {}".format(e))
		time.sleep(5)
client.on_disconnect = on_disconnect

client.connect(MQTT_BROKER, MQTT_PORT, keepalive=120)
client.subscribe(MQTT_TOPIC)

print("Scarecrow MQTT motion listener active. Waiting for trigger...")
idle_position()
client.loop_forever()
