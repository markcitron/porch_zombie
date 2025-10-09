#!/usr/bin/python3

import time
import paho.mqtt.client as mqtt
from gpiozero import LED, MotionSensor

# MQTT setup
MQTT_BROKER = "10.10.0.170"  # Change for production
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
TRIGGER_KEYWORD = "scarecrow"

# set up spst switches 
relay_1 = LED(5)
relay_2 = LED(6)
relay_3 = LED(13)
relay_4 = LED(19)
relay_5 = LED(26)
relay_6 = LED(21)
relay_7 = LED(20)
relay_8 = LED(16)
# motion = MotionSensor(17)

# Placeholder functions for linear actuators
def idle_position():
	# Set both actuators to idle position
	print("Setting Switches to off position.")
	relay_1.off()
	relay_2.off()
	relay_3.off()
	relay_4.off()
	relay_5.off()
	relay_6.off()
	relay_7.off()
	relay_8.off()
	return True

def someone_is_here():
	print("Someone is here!")
	return True

def active_motion():
	someone_is_here()
	time.sleep(30)
	idle_position()

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

print("Crypt Keeper MQTT motion listener active. Waiting for trigger...")
idle_position()
client.loop_forever()
