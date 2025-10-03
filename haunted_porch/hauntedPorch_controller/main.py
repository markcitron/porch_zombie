from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import paho.mqtt.client as mqtt

app = FastAPI()

# MQTT setup

mqtt_broker = "localhost"  # Change to your broker address
mqtt_port = 1883
mqtt_topic = "hauntedporch/control"
client = mqtt.Client()
broker_connected = False
try:
	client.connect(mqtt_broker, mqtt_port)
	broker_connected = True
except Exception as e:
	print(f"Warning: Could not connect to MQTT broker at {mqtt_broker}:{mqtt_port}. Error: {e}")

@app.get("/", response_class=HTMLResponse)
def read_root():
	return """
	<html>
		<head><title>Haunted Porch Controller</title></head>
		<body>
			<h1>Haunted Porch Controller</h1>
			<form action=\"/trigger\" method=\"post\">
				<label>Device:</label>
				<select name=\"device\">
					<option value=\"zombie_eyes\">Zombie Eyes</option>
					<option value=\"creepy_skull\">Creepy Skull</option>
					<option value=\"servo\">Servo</option>
				</select>
				<button type=\"submit\">Trigger</button>
			</form>
		</body>
	</html>
	"""

@app.post("/trigger")
def trigger(device: str = Form(...)):
	# Publish MQTT message
	if broker_connected:
		try:
			client.publish(mqtt_topic, device)
		except Exception as e:
			print(f"Error publishing to MQTT: {e}")
	else:
		print("MQTT broker not connected. Message not sent.")
	return RedirectResponse("/", status_code=303)
