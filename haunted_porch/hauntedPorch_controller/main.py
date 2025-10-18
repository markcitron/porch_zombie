from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import paho.mqtt.client as mqtt

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# MQTT setup

mqtt_broker = "10.10.0.170"  # Change to your broker address
mqtt_port = 1883
mqtt_topic = "hauntedporch/control"
client = mqtt.Client()
broker_connected = False
try:
	client.connect(mqtt_broker, mqtt_port, keepalive=60)
	client.loop_start()  # Start network loop for keepalive and auto-reconnect
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
				<label style="font-size:1.5em;padding-right:0.5em;">Device:</label>
				<select name="device" style="font-size:1.3em;padding:0.4em 1em;min-width:160px;">
					<option value="coffin_skeleton">Skeleton Coffin</option>
					<option value="creepy_skull">Creepy Skull</option>
					<option value="scarecrow">Scarecrow</option>
					<option value="electro_closet">Electro Closet</option>
					<option value="tilting_alien">Tilting Alien</option>
					<option value="crypt_keeper_1">Crypt Keeper 1</option>
					<option value="crypt_keeper_2">Crypt Keeper 2</option>
					<option value="crypt_keeper_3">Crypt Keeper 3</option>
					<option value="crypt_keeper_4">Crypt Keeper 4</option>
					<option value="crypt_keeper_5">Crypt Keeper 5</option>
					<option value="crypt_keeper_6">Crypt Keeper 6</option>
					<option value="crypt_keeper_7">Crypt Keeper 7</option>
					<option value="crypt_keeper_8">Crypt Keeper 8</option>
				</select>
				<button type="submit">Trigger</button>
			</form>
		</body>
	</html>
	"""

@app.post("/trigger")
def trigger(device: str = Form(...)):
	# Publish MQTT message
	global broker_connected
	if broker_connected:
		try:
			result = client.publish(mqtt_topic, device)
			if result.rc != mqtt.MQTT_ERR_SUCCESS:
				print(f"Publish failed with code {result.rc}, attempting reconnect...")
				client.reconnect()
				client.publish(mqtt_topic, device)
		except Exception as e:
			print(f"Error publishing to MQTT: {e}. Attempting reconnect...")
			try:
				client.reconnect()
				client.publish(mqtt_topic, device)
			except Exception as e2:
				print(f"Reconnect failed: {e2}")
				broker_connected = False
	else:
		print("MQTT broker not connected. Message not sent.")
	return RedirectResponse("/", status_code=303)
