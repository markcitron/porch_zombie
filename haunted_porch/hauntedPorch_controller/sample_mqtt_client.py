import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"  # Change to your broker address
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Received message on {msg.topic}: {msg.payload.decode()}")
    # Here you can add code to trigger your device's action

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(MQTT_TOPIC)

print("Listening for haunted porch commands...")
client.loop_forever()
