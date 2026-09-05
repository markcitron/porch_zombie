# Crypt Keeper Bot

The Crypt Keeper bot controls up to 8 relays for lights, effects, and actuators in your haunted porch setup. It listens for MQTT triggers and activates the appropriate relay(s) when commanded.

## Features
- Listens for MQTT messages on the topic `hauntedporch/control`.
- Supports up to 8 relays, each individually addressable.
- Prevents overlapping relay actions using threading locks.
- Can be triggered manually or as part of an automated sequence.

## Main Script
- `mqtt_crypt_keeper.py`: Main MQTT listener and relay controller.

## Requirements
- Python 3.7+
- Raspberry Pi with GPIO pins connected to relays
- Python modules:
  - `paho-mqtt`
  - `gpiozero`
  - `threading` (standard library)
- MQTT broker (e.g., Mosquitto) running on your network

Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-gpiozero
pip3 install paho-mqtt
```

## Usage
1. Edit `mqtt_crypt_keeper.py` to set the correct `MQTT_BROKER` IP address for your network.
2. Run the script on your Raspberry Pi:
   ```bash
   python3 mqtt_crypt_keeper.py
   ```
3. Send MQTT messages to the topic `hauntedporch/control` with payloads like `crypt_keeper_1`, `crypt_keeper_2`, ..., `crypt_keeper_8` to trigger the corresponding relay.

## Systemd Service (Optional)
To run the bot automatically on boot, create a systemd service:
```ini
[Unit]
Description=Crypt Keeper MQTT Relay Controller
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/porch_zombie/crypt_keeper/mqtt_crypt_keeper.py
WorkingDirectory=/home/pi/porch_zombie/crypt_keeper
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```
Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable crypt_keeper
sudo systemctl start crypt_keeper
```

## Troubleshooting
- Ensure your relays are wired correctly to the GPIO pins specified in the script.
- Check that your MQTT broker is running and reachable from the Pi.
- Use `systemctl status crypt_keeper` to check the service status if running as a service.

## Future Plans
- Add support for more advanced effects and sensors.
- Integrate with additional triggers (e.g., OpenCV, LIDAR).
