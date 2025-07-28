import time
import yaml
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

# Load sequence config
with open("sequence.yaml") as f:
    sequence = yaml.safe_load(f)["sequences"]["entry"]

def trigger_sequence():
    for step in sequence:
        client.publish(f"haunt/trigger/{step['bot']}", "go")
        time.sleep(step["delay"])

# Inside OpenCV motion detection:
# if motion detected in zone:
trigger_sequence()
