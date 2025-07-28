import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    if msg.topic == "haunt/trigger/spider":
        perform_sequence()

def perform_sequence():
    print("Spider jumps!")
    # Activate actuator, play sound, etc.

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("haunt/trigger/spider")
client.loop_forever()
