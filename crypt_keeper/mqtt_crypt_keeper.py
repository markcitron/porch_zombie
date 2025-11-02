#!/usr/bin/python3

import time
import paho.mqtt.client as mqtt
from gpiozero import LED, MotionSensor
import threading

# MQTT setup
# MQTT_BROKER = "10.10.0.170"  # Change for production
MQTT_BROKER = "10.10.0.175"  # point to Mad Scientist
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
TRIGGER_KEYWORD = "crypt_keeper"

# set up spst switches 
relay_1 = LED(5)
relay_2 = LED(6)
relay_3 = LED(13)
relay_4 = LED(16)
relay_5 = LED(19)
relay_6 = LED(20)
relay_7 = LED(21)
relay_8 = LED(26)
# motion = MotionSensor(17)

# Add lock to prevent overlapping switch actions
relay_locks = [threading.Lock() for _ in range(8)]

# Individual relay trigger handlers
def trigger_relay(relay, lock, relay_num):
    if not lock.acquire(blocking=False):
        print("Relay {} motion already active, ignoring trigger.".format(relay_num))
        return
    try:
        if relay_num == 3:
            time.sleep(10)
        print("Triggering relay {relay_num}")
        relay.on()
        time.sleep(1)
        relay.off()
        time.sleep(1)
    finally:
        lock.release()

def trigger_relay_1(): trigger_relay(relay_1, relay_locks[0], 1)
def trigger_relay_2(): trigger_relay(relay_2, relay_locks[1], 2)
def trigger_relay_3(): trigger_relay(relay_3, relay_locks[2], 3)
def trigger_relay_4(): trigger_relay(relay_4, relay_locks[3], 4)
def trigger_relay_5(): trigger_relay(relay_5, relay_locks[4], 5)
def trigger_relay_6(): trigger_relay(relay_6, relay_locks[5], 6)
def trigger_relay_7(): trigger_relay(relay_7, relay_locks[6], 7)
def trigger_relay_8(): trigger_relay(relay_8, relay_locks[7], 8)

# MQTT callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print("Received MQTT: {}".format(payload))
    if payload == "crypt_keeper_1":
        trigger_relay_1()
    elif payload == "crypt_keeper_2":
        trigger_relay_2()
    elif payload == "crypt_keeper_3":
        trigger_relay_3()
    elif payload == "crypt_keeper_4":
        trigger_relay_4()
    elif payload == "crypt_keeper_5":
        trigger_relay_5()
    elif payload == "crypt_keeper_6":
        trigger_relay_6()
    elif payload == "crypt_keeper_7":
        trigger_relay_7()
    elif payload == "crypt_keeper_8":
        trigger_relay_8()
    else:
        print("Unknown trigger: {}".format(payload))

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
client.loop_forever()
