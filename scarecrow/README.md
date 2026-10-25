# Scarecrow Bot

The Scarecrow bot controls relay(s) for movement or effects in your haunted porch setup.
The main MQTT listener coordinates base rotation, ultrasonic distance checks,
and the arm/hand grab action in one process.

## Features
- Listens for MQTT messages on the topic `hauntedporch/control`.
- Extends relay 6 (1) on `HP_new_visitor` and enables distance-triggered grabs.
- Grabs at 80 cm or closer, holds five seconds after grab completes, and releases.
- On `HP_theyre_gone`, finishes any running grab, skips any remaining hold,
  releases, then contracts relay 6 (0) and waits for the next group.
- Starts and shuts down released with relay 6 contracted (0).
- Keeps MQTT responsive during actions, queues commands in arrival order,
  and re-subscribes after reconnection.

## Main Script
- `scarecrow_listening_mqtt.py`: Combined visitor-event and distance controller.

## Requirements
- Python 3.7+
- Raspberry Pi with the existing relay controller connected
- Python modules:
  - `paho-mqtt` 2.x
  - `lib8relind` (the same relay-controller library used by `test_relays.py`)
  - `robot_hat` (the same sensor/servo library used by the action/distance tests)
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
   warm-up, motion sends `HP_new_visitor`, setting relay 6 to 1 and enabling
   distance-triggered grabs. `HP_theyre_gone` releases before returning the
   base to 0. Repeated arrivals do not restart the hold, re-arm the distance
   trigger, or restart the base settling delay.

**Run only this combined controller on the Scarecrow Pi. Do not also run
`scarecrow_waiting.py`, relay tests, or manual action scripts.** It reuses their
libraries and helpers without launching a second hardware-control process.

### Combined motion sequence and configuration

- Initializes the Robot HAT once, contracts the base, and releases the hands
  and arms on startup.
- Accepts MQTT commands immediately after initialization, but allows no grabs
  during the 15-second startup grace period.
- While the base is extended, reads the ultrasonic sensor on TRIG `D2` /
  ECHO `D3`. A valid distance of **80 cm or closer** triggers the existing
  `grab`, including its timed relay 3 sound trigger.
- Holds for five seconds after `grab` finishes, then calls `let_go`. A valid
  distance **beyond 80 cm** is required before another grab in that session.
  Invalid readings/timeouts neither trigger nor re-arm a grab.
- A departure received during a grab is queued: the grab finishes, the
  remaining hold is skipped, `let_go` completes, and only then does the base
  contract. A departure during the hold also releases before returning the
  base. MQTT remains responsive during these actions.
- Remains running with the base contracted until the next arrival. A new
  session re-arms the distance trigger. Departures and subsequent arrivals
  are processed in order, not merged.

The combined controller imports `TRIGGER_DISTANCE_CM` (currently `80.0`),
`STARTUP_DELAY_SECONDS` (`15.0`), and `HOLD_SECONDS` (`5.0`) from
`scarecrow_waiting.py`, so these settings remain shared. It uses
`READ_INTERVAL` (`0.2` seconds) from `test_distance_ultra.py`.
`BASE_SETTLE_SECONDS` is configured in `scarecrow_listening_mqtt.py` and
defaults to **0.0**, as requested. Increase it if the base needs time to
finish rotating before grabs are allowed. Neither the relay command nor a
fixed delay is physical position feedback.

MQTT callbacks only enqueue events; the main control thread owns base and
arm/hand sequencing. The existing sound trigger still runs alongside grab.
Relay reads/writes, including sound, share an in-process lock in `relays.py`
to serialize controller transactions. The lock is not held during movement
delays and does not protect against separately launched processes.

As requested, **loss of the MQTT connection leaves relay 6 unchanged** while
the network loop reconnects; distance-triggered grabs remain enabled if the
base was extended. Reconnection does not reset it. These are
non-retained events, not synchronized state: events sent while disconnected
or before the listener subscribes may be missed. If a departure is missed,
relay 6 can remain at 1 until a new departure command or script shutdown.
Start the listener before the PIR publisher for testing. Initial connection
failure or a rejected connection/subscription surfaces as an error and exits.

Unrelated payloads, invalid UTF-8, and retained messages are logged and ignored,
so an old retained arrival cannot move the base on startup. Network-worker
errors are surfaced to the main thread rather than silently killing MQTT
reception. Ctrl+C, or an error that unwinds the controller, stops MQTT and
attempts release before contracting the base. A base reset and disconnect
are still attempted if release fails. Power loss or a forced process kill
cannot run this cleanup.

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

This is the legacy standalone mode, not a companion to the combined MQTT
controller. It still exits when relay 6 reads 0. For repeated MQTT visitor
sessions, use only `scarecrow_listening_mqtt.py` instead.

Run on the Raspberry Pi from the `scarecrow` directory:

```bash
python3 scarecrow_waiting.py
```

This uses the same `robot_hat` and `lib8relind` hardware libraries and
configuration as `test_actions.py`, `test_relays.py`, and
`test_distance_ultra.py`. The ultrasonic sensor uses TRIG `D2` and ECHO `D3`.
No MQTT connection is required for this mode.

- Waits 15 seconds after hardware initialization before checking distances.
- Grabs at **80 cm or closer**, only while relay **6** reads **1**.
- Holds for five seconds after `grab` finishes, then calls `let_go`.
- Requires a valid reading **beyond 80 cm** before another grab is allowed.
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
Description=Scarecrow MQTT and Distance Controller
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
