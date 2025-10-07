#!/usr/bin/python3

#
# MQTT Coffin Scarecrow and Electro Closet Control
# Uses relays to control linear actuators for both devices
# 
# Coffin Skeleton: Relay 1 (up/down)
# Electro Closet: Relay 2 & 3 (open/close door) - Electro Zombie is motion triggered (for now)
#

import time
import paho.mqtt.client as mqtt
import threading
from relays import *

# Lock to prevent overlapping motions
motion_lock = threading.Lock()

# MQTT setup
MQTT_BROKER = "10.10.0.170"  # Change for production
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
TRIGGER_KEYWORD1 = "coffin_skeleton"
TRIGGER_KEYWORD2 = "electro_closet"

# set up linear actuator relays
relay1 = LinAct("Coffin Skeleton", 26)  # Coffin Skeleton
relay2 = LinAct("Electro Closet", 20)  # Electro Closet - left door
relay3 = LinAct("Electro Closet", 21)  # Electro Closet - Right door

def idle_position():
	# Set actuators to idle position
	print("Setting actuators to idle position.")
	relay1.contract()
	time.sleep(.1)
	relay2.contract()
	time.sleep(.1)
	relay3.contract()
	time.sleep(.1)
	return True

def someone_is_here():
	print("Someone is here!")
	relay6.contract() 
	time.sleep(3) 
	relay1.contract() 
	time.sleep(3)
	relay1.extend() 
	time.sleep(5)
	relay1.contract()
	time.sleep(3)
	relay1.extend()
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
	print("MQTT disconnected with code {}. Attempting reconnect...".format(rc))
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
