# Scarecrow Bot

The Scarecrow bot controls relay(s) for movement or effects in your haunted porch setup.
The MQTT listener below controls only relay 6, which rotates the base.

## Features
- Listens for MQTT messages on the topic `hauntedporch/control`.
- Extends relay 6 (1) on `HP_new_visitor` and contracts it (0) on `HP_theyre_gone`.
- Starts with relay 6 contracted (0) and contracts it again on normal shutdown
  or a Python exception.
- Handles MQTT messages sequentially and re-subscribes after reconnection.

## Main Script
- `scarecrow_listening_mqtt.py`: Visitor-event listener for the base relay.

## Requirements
- Python 3.7+
- Raspberry Pi with the existing relay controller connected
- Python modules:
  - `paho-mqtt` 2.x
  - `lib8relind` (the same relay-controller library used by `test_relays.py`)
- Other action/distance scripts also require the existing `robot_hat` library.
- MQTT broker (e.g., Mosquitto) running on your network

Use the Pi environment in which the relay tests already work. If a new virtual
environment is needed, run from the `scarecrow` directory:

```bash
sudo apt update
sudo apt install python3-venv
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install --upgrade "paho-mqtt>=2,<3"
```

The system-site-packages option exposes system-installed hardware libraries;
if `lib8relind` is installed in a different environment, use that environment
instead. Do not use `sudo pip` or `--break-system-packages`.

## Usage
1. The listener defaults to broker `10.10.0.175:1883` and topic
   `hauntedporch/control`, matching `madscientist/waiting_for_visitors_MQTT.py`.
2. Start the listener on the Scarecrow Pi:
   ```bash
   .venv/bin/python scarecrow_listening_mqtt.py
   ```
3. Wait for `Listening for visitor events on hauntedporch/control`.
4. Run `waiting_for_visitors_MQTT.py` on the Mad Scientist Pi. After its PIR
   warm-up, motion sends `HP_new_visitor`, setting relay 6 to 1. The listener
   holds that state until `HP_theyre_gone` sets it to 0. Repeated copies of
   either message simply set the same relay value again.

The listener uses `relays.LinAct` directly; it does not reset the servo
controller, move the arms/hands, trigger sound, or start `scarecrow_waiting.py`.
For this base-only test, stop other scripts that can change relay 6.

As requested, **loss of the MQTT connection leaves relay 6 unchanged** while
the network loop reconnects. Reconnection does not reset it. These are
non-retained events, not synchronized state: events sent while disconnected
or before the listener subscribes may be missed. If a departure is missed,
relay 6 can remain at 1 until a new departure command or script shutdown.
Start the listener before the PIR publisher for testing. Initial connection
failure or a rejected connection/subscription surfaces as an error and exits.

Unrelated payloads, invalid UTF-8, and retained messages are logged and ignored,
so an old retained arrival cannot move the base on startup. Only relay 6 is
written. Ctrl+C, or an error that unwinds the main loop, attempts to contract
it before disconnecting. Power loss or a forced process kill cannot run this
cleanup.

### Manual MQTT test

If `mosquitto_pub` is available, send these from a machine that can reach the
broker. Do not add `-r` (retain):

```bash
mosquitto_pub -h 10.10.0.175 -t hauntedporch/control -q 1 -m HP_new_visitor
mosquitto_pub -h 10.10.0.175 -t hauntedporch/control -q 1 -m HP_theyre_gone
```

Keep the movement area clear during testing.

Hardware-free listener tests:

```bash
python3 -m unittest discover -s tests -p test_scarecrow_listening_mqtt.py
```

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
Description=Scarecrow Visitor MQTT Base Relay
After=network.target

[Service]
ExecStart=/home/pi/repos/porch_zombie/scarecrow/.venv/bin/python /home/pi/repos/porch_zombie/scarecrow/scarecrow_listening_mqtt.py
WorkingDirectory=/home/pi/repos/porch_zombie/scarecrow
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
- Ensure the relay controller is connected as for the existing relay tests.
- Check that your MQTT broker is running and reachable from the Pi.
- Use `systemctl status scarecrow` to check the service status if running as a service.

## Future Plans
- Add support for more advanced effects and sensors.
- Integrate with additional triggers (e.g., OpenCV, LIDAR).
