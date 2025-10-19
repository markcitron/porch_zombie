# Scarecrow Bot

The Scarecrow bot controls relay(s) for movement or effects in your haunted porch setup. It listens for MQTT triggers and activates the relay(s) when commanded.

## Features
- Listens for MQTT messages on the topic `hauntedporch/control`.
- Controls relay(s) for scarecrow movement or effects.
- Prevents overlapping relay actions using threading locks.
- Can be triggered manually or as part of an automated sequence.

## Main Script
- `mqtt_scarecrow.py`: Main MQTT listener and relay controller.

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
1. Edit `mqtt_scarecrow.py` to set the correct `MQTT_BROKER` IP address for your network.
2. Run the script on your Raspberry Pi:
   ```bash
   python3 mqtt_scarecrow.py
   ```
3. Send MQTT messages to the topic `hauntedporch/control` with payload `scarecrow` to trigger the scarecrow relay(s).

## Systemd Service (Optional)
To run the bot automatically on boot, create a systemd service:
```ini
[Unit]
Description=Scarecrow MQTT Relay Controller
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/porch_zombie/scarecrow/mqtt_scarecrow.py
WorkingDirectory=/home/pi/porch_zombie/scarecrow
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
sudo systemctl enable scarecrow
sudo systemctl start scarecrow
```

## Troubleshooting
- Ensure your relays are wired correctly to the GPIO pins specified in the script.
- Check that your MQTT broker is running and reachable from the Pi.
- Use `systemctl status scarecrow` to check the service status if running as a service.

## Future Plans
- Add support for more advanced effects and sensors.
- Integrate with additional triggers (e.g., OpenCV, LIDAR).
