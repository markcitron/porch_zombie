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
		<head>
			<title>Haunted Porch Controller</title>
			<style>
				body {
					background: #222 url('/static/ghost.png') no-repeat top right;
					background-size: 200px;
					color: #eee;
					font-family: 'Creepster', cursive, sans-serif;
					text-shadow: 2px 2px 8px #000;
				}
				h1 {
					font-size: 2.5em;
					letter-spacing: 2px;
					margin-bottom: 0.5em;
				}
				form {
					background: rgba(0,0,0,0.7);
					padding: 1em 2em;
					border-radius: 10px;
					box-shadow: 0 0 20px #000;
					display: inline-block;
				}
				button {
					background: #444;
					color: #fff;
					border: none;
					padding: 0.5em 1.5em;
					border-radius: 5px;
					font-size: 1.2em;
					cursor: pointer;
					box-shadow: 0 0 10px #000;
				}
				button:hover {
					background: #666;
				}
			</style>
			<link href="https://fonts.googleapis.com/css?family=Creepster" rel="stylesheet">
		</head>
		<body>
			<h1>👻 Haunted Porch Controller 👻</h1>
			<img src="/static/ghost.png" alt="Creepy Ghost" style="width:150px;float:right;margin:0 0 2em 2em;filter:drop-shadow(0 0 10px #fff);">
			<form action="/trigger" method="post">
				<label>Device:</label>
				<select name="device">
					<option value="zombie_eyes">Zombie Eyes</option>
					<option value="creepy_skull">Creepy Skull</option>
					<option value="servo">Servo</option>
				</select>
				<button type="submit">Trigger</button>
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
