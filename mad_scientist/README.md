# Mad Scientist
This runs on the main trigger Raspberry Pi. It will detect motion and be the MQTT source to trigger the other bots.

## Files of Interest
- `mqtt_main_trigger.py` - Main motion-trigger script. Uses a PIR motion sensor on GPIO17 to detect motion and publishes a configurable sequence of MQTT triggers.
- `trigger_sequence.json` - External JSON config describing the trigger order and per-trigger delays. Edit this to control the timing and order of your props.
- `trigger_status.log` - Rotating log file containing timestamps and status messages for each published trigger.
- `ui.py` - Small FastAPI UI to view the last-run sequence, tail the status log and manually trigger individual devices.

## Dependencies
Install the required Python packages on the main trigger Pi:

```bash
sudo apt update
sudo apt install -y python3-pip python3-gpiozero
pip3 install paho-mqtt fastapi uvicorn
```

Note: If you prefer to avoid installing the UI dependencies on the trigger Pi, you can run `ui.py` on a separate machine that can reach the MQTT broker.

## Configuration
Edit `trigger_sequence.json` to change the order and inter-trigger delays. The file format:

```json
{
  "sequence": [
    { "device": "coffin_skeleton", "delay_after": 1.5 },
    { "device": "creepy_skull", "delay_after": 0.5 }
  ]
}
```

- `device` is the MQTT payload that corresponds to a device script (see controller UI for names).
- `delay_after` is how many seconds to wait AFTER publishing this device before publishing the next device.

The `mqtt_main_trigger.py` script will prefer the JSON file if present; otherwise it falls back to a built-in default sequence.

## Running the Trigger Script
Start the motion trigger (connects to broker at `10.10.0.175` by default):

```bash
python3 mqtt_main_trigger.py
```

The script will:
- Connect to MQTT broker at `10.10.0.175:1883` (configurable inside the script).
- Start the PIR loop (GPIO17) using `gpiozero.MotionSensor`.
- On motion detection, publish the configured trigger sequence and log the events.

## Running the UI
Start the UI server (separate process):

```bash
uvicorn mad_scientist.ui:app --host 0.0.0.0 --port 8080
```

Open in a browser:
```
http://<pi_ip>:8080/
```

UI features:
- Shows the configured trigger sequence and per-trigger delay.
- Displays a tail of the status log (updates every 5s).
- Buttons to publish individual triggers for testing.

## Logs
The script writes `trigger_status.log` in the same directory. It uses a rotating logger (2MB per file, 3 backups) and also prints to console.

## Systemd Service (optional)
Create a systemd unit to run the trigger script at boot:

Create `/etc/systemd/system/porch-trigger.service` with:

```ini
[Unit]
Description=Porch Motion Trigger
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/pi/Development/porch_zombie/mad_scientist
ExecStart=/usr/bin/python3 mqtt_main_trigger.py
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable porch-trigger.service
sudo systemctl start porch-trigger.service
```

Create a systemd unit for the UI (optional):

```ini
[Unit]
Description=Porch Trigger UI
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/pi/Development/porch_zombie/mad_scientist
ExecStart=/usr/local/bin/uvicorn mad_scientist.ui:app --host 0.0.0.0 --port 8080
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
```

## Notes & Troubleshooting
- Ensure GPIO pin 17 is wired to your PIR sensor. Test `gpiozero` and sensor separately first.
- MQTT broker must be reachable at the configured IP address. The UI and trigger script each use their own MQTT client.
- The trigger sequence timing is important: make small adjustments and test components individually via the UI before running a full sequence.
- If `gpiozero` is not available, the trigger script will log an error and exit; you can implement a fallback GPIO reader if needed.

If you want any refinements (test pages, status API, or confirmation ack flows), tell me which feature to add next.
