#!/usr/bin/python3

import time
import paho.mqtt.client as mqtt
import threading
from relays import *

# MQTT Setup
# Shared Mosquitto broker
MQTT_BROKER = "10.10.0.175"
MQTT_PORT = 1883
MQTT_TOPIC = "porch_zombie/hauntedporch"
TRIGGER_KEYWORD1 = "zc_open"
TRIGGER_KEYWORD2 = "zc_close"
TRIGGER_KEYWORD3 = "cs_lower"
TRIGGER_KEYWORD4 = "cs_raise"

# set up relays
zombie_closet = LinAct("Zombie Closet", 26)
coffin_skeleton = LinAct("Coffin Skeleton", 20)
third_trigger = LinAct("Third Trigger", 21)

def idle_position():
    zombie_closet.close()
    coffin_skeleton.lower()
    third_trigger.reset()
    return True

def zc_open():
    zombie_closet.extend()
    return True

def zc_close():
    zombie_closet.contract()
    return True

def cs_lower():
    coffin_skeleton.extend()
    return True

def cs_raise():
    coffin_skeleton.contract()
    return True

# MQTT Callback
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    if message == TRIGGER_KEYWORD1:
        zc_open()
    elif message == TRIGGER_KEYWORD2:
        zc_close()
    elif message == TRIGGER_KEYWORD3:
        cs_lower()
    elif message == TRIGGER_KEYWORD4:
        cs_raise()
    else:
        idle_position()

# add disconnect handler for auto-reconnect
def on_disconnect(client, userdata, rc):
    print("MQTT disconnected with code{}. Attempting reconnect ...".format(rc))
    while rc != 0:
        try:
            client.reconnect()
            if rc == 0:
                print("MQTT reconnected successfully.")
        except Exception as e:
            print("Reconnect failed: {}".format(e))
        time.sleep(5)

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=120)
client.subscribe(MQTT_TOPIC)
print("Listening for MQTT messages on topic:", MQTT_TOPIC)
idle_position()
client.loop_forever()