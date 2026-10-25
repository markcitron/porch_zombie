# Zombie Closet

## MQTT visitor sequence

Run `zombiecloset_mqtt_listener.py` on the Zombie Closet Raspberry Pi. It
subscribes to `hauntedporch/control` on broker **10.10.0.175:1883**, matching
the Mad Scientist visitor publisher.

1. `HP_new_visitor` schedules a sequence after **10 seconds**.
2. The sequence calls the existing `activate_sidekick()` from
   `zombie_closet.py`, the same action used by `test_zombie_closet.py`.
3. The sidekick relay uses **BCM GPIO 20** and stays active for its existing
   **10-second activation time**, then resets.
4. A `TODO` comment after that call marks where future sequence steps belong.

The pre-action delay is configured with `VISITOR_DELAY_SECONDS` at the top
of the listener. It is separate from `SIDEKICK_ACTIVATION_TIME` in
`zombie_closet.py`.

### Visitor sessions and concurrency

- Only the first arrival per session schedules a sequence. Further arrivals
  in that session are ignored, including duplicates after the sequence ends.
- `HP_theyre_gone` re-arms arrival detection for the next session. As
  requested, it **does not cancel a scheduled activation**, including during
  the delay or an action.
- New sessions arriving while a sequence is busy are queued. Sequences never
  overlap. Their delay is measured from MQTT receipt; an overdue sequence
  starts after the previous one finishes, rather than adding another delay.
- MQTT runs in a background network thread; callbacks only enqueue timestamped
  events. Delays and hardware actions do not block message reception.
- Reconnection re-subscribes without clearing session state or pending work.
  Commands sent during an outage may be missed because this uses non-retained
  events, not synchronized state. A missed departure can prevent re-arming
  until another departure is received or the script is restarted.
- Retained events, unrelated payloads/topics, and invalid UTF-8 are logged and
  ignored. Paho callback API v2 is used.

### Setup and running

Use the environment where `test_zombie_closet.py` already works. If you need
a new virtual environment, run on the Pi from the `zombiecloset` directory:

```bash
sudo apt update
sudo apt install python3-venv
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install --upgrade "paho-mqtt>=2,<3"
.venv/bin/python -c "import RPi.GPIO; import paho.mqtt.client; print('GPIO and MQTT imports OK')"
.venv/bin/python zombiecloset_mqtt_listener.py
```

The system-site-packages option makes system-installed GPIO libraries
available. Do not use `sudo pip` or `--break-system-packages`. Do not run
manual relay/action tests alongside this listener.

Start the listener before the Mad Scientist publisher and wait for
`Listening for visitor events on hauntedporch/control`.

The closet is closed on startup and shutdown. The sidekick action resets its
own relay even if interrupted or it raises an error; failures are propagated,
not swallowed. MQTT/GPIO errors stop the script and attempt cleanup. Ctrl+C
stops pending work, closes the closet, and cleans up GPIO. A forced kill or
power loss cannot run cleanup.

### Manual MQTT test

With the movement area clear, use `mosquitto_pub` if installed. Do not add
`-r` (retain):

```bash
mosquitto_pub -h 10.10.0.175 -t hauntedporch/control -q 1 -m HP_new_visitor
mosquitto_pub -h 10.10.0.175 -t hauntedporch/control -q 1 -m HP_theyre_gone
```

After sending arrival, expect the sidekick to activate after 10 seconds,
then remain active for another 10 seconds. Send departure before testing a
second arrival.

Hardware-free tests:

```bash
python3 -m unittest discover -s tests -p test_zombiecloset_mqtt_listener.py
```