# Haunted Porch Controller

This is a simple FastAPI-based controller app for my haunted porch Halloween project. It provides a web UI to trigger MQTT messages to your porch devices.

## Setup

1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```powershell
   uvicorn main:app --reload
   ```
   (Run this command from the `hauntedPorch_controller` directory)

3. Open your browser and go to:
   ```
   http://localhost:8000/
   ```
   Use the web UI to trigger device actions.

## Sample MQTT Client

See `sample_mqtt_client.py` for a template to use on your porch devices. This script listens for MQTT messages and can trigger device actions.

## Configuration
- Change `mqtt_broker` in `main.py` and `sample_mqtt_client.py` to match your MQTT broker address if not running locally.
- Add or modify device options in the HTML form in `main.py` as needed.


## Mosquitto (MQTT Broker) Setup

### Windows (Development)
1. Download Mosquitto from the official site: https://mosquitto.org/download/
2. Run the installer and follow the prompts.
3. After installation, open PowerShell and start Mosquitto with:
   ```powershell
   mosquitto
   ```
   (You may need to add Mosquitto to your PATH or run from its install directory.)

### Raspberry Pi (Production)
1. Open a terminal on your Pi.
2. Install Mosquitto and its clients:
   ```bash
   sudo apt update
   sudo apt install mosquitto mosquitto-clients
   ```
3. Start Mosquitto:
   ```bash
   sudo systemctl start mosquitto
   sudo systemctl enable mosquitto
   ```
   Mosquitto will now run as a service.

### Testing Mosquitto
On either system, you can test with:
```bash
mosquitto_sub -h localhost -t hauntedporch/control
mosquitto_pub -h localhost -t hauntedporch/control -m "test"
```
Your FastAPI app and sample client should now connect to the broker.

---
- Ensure your MQTT broker is running and accessible.
- Devices should subscribe to the topic specified in `main.py` (`hauntedporch/control`).
