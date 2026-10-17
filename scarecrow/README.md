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

### Testing combined actions

The arm and hand controls are shared by `scarecrow_actions.py`. Use
`test_actions.py` to run either combined action:

```bash
python3 test_actions.py grab
python3 test_actions.py let go
```

`grab` closes the arms, waits 0.5 seconds, and closes both hands. `let go`
opens the arms, waits 0.5 seconds, and opens both hands.

Each `grab` also triggers the external sound speaker on relay **3** in
parallel with the arm/hand movement: relay 3 is set to **0** at one second
after grab starts, then to **1** after another **0.5 seconds** (1.5 seconds
after grab starts). These are explicit controller values, independent of the
movement helpers' extend/contract naming. Timing is subject to normal OS and
hardware scheduling delays. `grab` waits for both movement and the sound
trigger to finish, and reports any sound-trigger error. `let_go` does not
trigger sound. This applies to both manual actions and distance-triggered mode.

### Distance-triggered waiting mode

Run on the Raspberry Pi from the `scarecrow` directory:

```bash
python3 scarecrow_waiting.py
```

This uses the same `robot_hat` and `lib8relind` hardware libraries and
configuration as `test_actions.py`, `test_relays.py`, and
`test_distance_ultra.py`. The ultrasonic sensor uses TRIG `D2` and ECHO `D3`.
No MQTT connection is required for this mode.

- Waits 15 seconds after hardware initialization before checking distances.
- Grabs at **50 cm or closer**, only while relay **6** reads **1**.
- Holds for five seconds after `grab` finishes, then calls `let_go`.
- Requires a valid reading **beyond 50 cm** before another grab is allowed.
  Sensor timeouts and invalid distances neither trigger nor re-arm it.
- Monitors relay 6 every 0.2 seconds, including during startup, actions, and
  the hold. Any observed **0** latches shutdown even if the relay turns on
  again: a running action finishes, the remaining hold is skipped, and
  `let_go` runs before exit. Relay-off during startup also releases and exits.
- Ctrl+C or a sensor/controller error also attempts `let_go` before exit;
  hardware errors are surfaced rather than ignored.

Polling cannot detect an off/on pulse shorter than the polling/read interval.
Test with the movement area clear before allowing visitors near the prop.

The automated waiting-mode tests use mocked hardware:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

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
