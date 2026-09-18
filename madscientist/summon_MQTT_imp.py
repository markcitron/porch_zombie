#!/usr/bin/python3
"""Publish Zombie Closet test commands from a four-key USB keyboard.

This script targets Raspberry Pi OS on a Raspberry Pi Zero. It connects to the
shared Mosquitto broker and sends one command for each 1-4 key press.
"""

import os
import socket

from evdev import InputDevice, categorize, ecodes, list_devices
import paho.mqtt.client as mqtt


MQTT_BROKER = "10.10.0.175"
MQTT_PORT = 1883
MQTT_TOPIC = "porch_zombie/hauntedporch"

# Set this to an explicit /dev/input/eventX path if automatic selection picks
# the wrong input device. It can also be set with the KEYBOARD_DEVICE variable.
KEYBOARD_DEVICE = os.environ.get("KEYBOARD_DEVICE")

KEY_COMMANDS = {
	ecodes.KEY_1: "zc_open",
	ecodes.KEY_KP1: "zc_open",
	ecodes.KEY_2: "zc_close",
	ecodes.KEY_KP2: "zc_close",
	ecodes.KEY_3: "cs_lower",
	ecodes.KEY_KP3: "cs_lower",
	ecodes.KEY_4: "cs_raise",
	ecodes.KEY_KP4: "cs_raise",
}

KEY_GROUPS = (
	{ecodes.KEY_1, ecodes.KEY_KP1},
	{ecodes.KEY_2, ecodes.KEY_KP2},
	{ecodes.KEY_3, ecodes.KEY_KP3},
	{ecodes.KEY_4, ecodes.KEY_KP4},
)


def find_keyboard():
	if KEYBOARD_DEVICE:
		return InputDevice(KEYBOARD_DEVICE)

	for device_path in list_devices():
		device = InputDevice(device_path)
		device_keys = set(device.capabilities().get(ecodes.EV_KEY, []))
		if all(device_keys.intersection(group) for group in KEY_GROUPS):
			return device

	raise RuntimeError(
		"No keyboard with keys 1-4 was found. Set KEYBOARD_DEVICE to its "
		"/dev/input/eventX path."
	)


def connect_mqtt():
	client_id = "sneaky-imp-{}".format(socket.gethostname())
	client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
	client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
	client.loop_start()
	return client


def publish_command(client, key_code):
	command = KEY_COMMANDS[key_code]
	message = client.publish(MQTT_TOPIC, command)
	message.wait_for_publish(timeout=5)
	if message.rc != mqtt.MQTT_ERR_SUCCESS:
		raise RuntimeError("MQTT publish failed with code {}".format(message.rc))
	print("Published: {}".format(command))


def main():
	keyboard = find_keyboard()
	client = connect_mqtt()
	print("Reading keys 1-4 from {} ({})".format(keyboard.path, keyboard.name))
	print("Publishing to {} on {}:{}".format(
		MQTT_TOPIC, MQTT_BROKER, MQTT_PORT
	))

	try:
		for event in keyboard.read_loop():
			if event.type != ecodes.EV_KEY:
				continue

			key_event = categorize(event)
			if key_event.keystate != key_event.key_down:
				continue

			key_code = event.code
			if key_code in KEY_COMMANDS:
				publish_command(client, key_code)
	finally:
		client.loop_stop()
		client.disconnect()
		keyboard.close()


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Stopped")
