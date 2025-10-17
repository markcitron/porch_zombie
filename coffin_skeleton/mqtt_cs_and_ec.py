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
coffin_lock = threading.Lock()
electro_lock = threading.Lock()
alien_lock = threading.Lock()

# MQTT setup
MQTT_BROKER = "10.10.0.170"  # Change for production
# MQTT_BROKER = "10.10.0.175"  # Point to Mad Scientist
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
TRIGGER_KEYWORD1 = "coffin_skeleton"
TRIGGER_KEYWORD2 = "electro_closet"
TRIGGER_KEYWORD3 = "tilting_alien"

# set up linear actuator relays
relay1 = LinAct("Coffin Skeleton", 26)  # Coffin Skeleton
relay2 = LinAct("Electro Closet", 20)  # Electro Closet - left & right door
relay3 = LinAct("Tilting Alien", 21)  # Electro Closet - Right door

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

def coffin_skeleton():
	if not coffin_lock.acquire(blocking=False):
		print("Coffin Skeleton motion already active, ignoring trigger.")
		return False
	try:
		print("Coffin Skeleton activated!")
		relay1.extend()  # Raise coffin
		time.sleep(20)   # Keep it up for 20 seconds
		relay1.contract()  # Lower coffin
		return True
	finally:
		coffin_lock.release()

def electro_closet():
	if not electro_lock.acquire(blocking=False):
		print("Electro Closet motion already active, ignoring trigger.")
		return False
	try:
		print("Electro Closet activated!")
		relay2.extend()  # Open left door
		time.sleep(30)   # Keep doors open for 30 seconds
		relay2.contract()  # Close left door
		return True
	finally:
		electro_lock.release()

def tilting_alien():
	if not alien_lock.acquire(blocking=False):
		print("Tilting Alien motion already active, ignoring trigger.")
		return False
	try:
		print("Tilting Alien activated!")
		relay3.extend()  # Tilt alien
		time.sleep(10)   # Keep it tilted for 10 seconds
		relay3.contract()  # Reset alien
		return True
	finally:
		alien_lock.release()

# MQTT callback
def on_message(client, userdata, msg):
	payload = msg.payload.decode()
	print("Received MQTT: {}".format(payload))
	if payload == TRIGGER_KEYWORD1:
		coffin_skeleton()
	elif payload == TRIGGER_KEYWORD2:
		electro_closet()
	elif payload == TRIGGER_KEYWORD3:
		tilting_alien()

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
