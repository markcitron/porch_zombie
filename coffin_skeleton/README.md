# Coffin Skeleton & Electro Closet MQTT Controller

This script (`mqtt_cs_and_ec.py`) provides MQTT-based remote control for two Halloween props:
- **Coffin Skeleton**: Raises and lowers a skeleton using a linear actuator (relay 1)
- **Electro Closet**: Opens and closes closet doors using two linear actuators (relays 2 & 3)

## What the Script Does
- Listens for MQTT messages on a specified topic.
- When a message with the payload `coffin_skeleton` is received, it triggers the Coffin Skeleton actuator to raise and then lower the skeleton.
- When a message with the payload `electro_closet` is received, it triggers both Electro Closet actuators to open and then close the doors.
- Includes logic to prevent overlapping motions using a threading lock.
- Automatically reconnects to the MQTT broker if the connection is lost.

## Requirements
- Python 3.7+
- `paho-mqtt` Python package
- `relays.py` module and hardware relay interface (see project for details)
- MQTT broker (e.g., Mosquitto)

Install Python dependencies:
```sh
pip install paho-mqtt typing_extensions
```

## Usage
1. Edit `mqtt_cs_and_ec.py` to set the correct `MQTT_BROKER` IP address for your network.
2. Run the script on your controller device:
   ```sh
   python3 mqtt_cs_and_ec.py
   ```
3. Send MQTT messages to the topic `hauntedporch/control` with payloads `coffin_skeleton` or `electro_closet` to trigger the props.

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
   Mosquitto will now run as a service and start automatically on boot.

## Notes
- Make sure your relays and actuators are wired and powered correctly before running the script.
- You can test MQTT messages using `mosquitto_pub` from another terminal or device:
  ```sh
  mosquitto_pub -h <broker_ip> -t hauntedporch/control -m coffin_skeleton
  ```
- Adjust relay pin numbers and logic in the script as needed for your hardware setup.
