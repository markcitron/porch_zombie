# Mad Scientist

## PIR input test

`test_pir.py` displays the raw digital output of an HC-SR501-compatible PIR
every 0.2 seconds, with a timestamp. It does not filter or debounce the signal.

### Wiring

With the Raspberry Pi powered off, connect:

- PIR OUT to **BCM GPIO 6**, physical header pin **31**.
- PIR GND to a Pi ground, for example physical pin **6**.
- PIR VCC to the module's specified supply. Standard HC-SR501 modules normally
  use the Pi's **5 V** supply, for example physical pin **2**.

Check your particular module's pin labels and supply requirements. The OUT
signal must be **3.3 V logic** for the Pi GPIO; never connect 5 V to GPIO 6.

### Running

Use a Raspberry Pi environment with the `RPi.GPIO` module available:

```bash
python3 test_pir.py
```

- Allow approximately **30-60 seconds** after sensor power-up for stabilization.
  The script prints immediately so startup fluctuations are visible.
- `PIR=1` means the sensor output is HIGH (motion signaled).
- `PIR=0` means the sensor output is LOW (idle output).
- With the jumper in **L** (non-retriggering) mode, output can drop LOW and
  enter a blocking interval even if someone is still moving. It is not a
  continuous presence or distance measurement.
- Press **Ctrl+C** to stop. The script releases only GPIO 6, leaving unrelated
  GPIO channels alone.

Hardware-free tests, run from this directory:

```bash
python3 -m unittest discover -s tests -p test_pir_input.py
```

## MQTT visitor monitor

`waiting_for_visitors_MQTT.py` uses the same PIR connection on **BCM GPIO 6**
(physical pin 31) to publish visitor-session events. It runs on the Mad
Scientist Pi at `10.10.0.175` and connects to the existing MQTT broker at
`10.10.0.175:1883`. A broker such as Mosquitto must already be running there;
this script is an MQTT publisher, not a broker.

Raspberry Pi OS protects its system Python and may reject a system-wide
`pip install` with `externally-managed-environment`. Use a project virtual
environment instead. From the `madscientist` directory on the Pi:

```bash
sudo apt update
sudo apt install python3-venv
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install --upgrade "paho-mqtt>=2,<3"
.venv/bin/python waiting_for_visitors_MQTT.py
```

`--system-site-packages` lets the environment use the system-installed GPIO
library that already runs `test_pir.py`, while Paho is installed separately
inside `.venv`. Do not use `sudo pip` or `--break-system-packages`.

For subsequent runs, only the last command is needed; activation is not
required when calling `.venv/bin/python` directly. Check both imports with:

```bash
.venv/bin/python -c "import RPi.GPIO; import paho.mqtt.client; print('GPIO and MQTT imports OK')"
```

Configuration constants are at the top of the script:

| Setting | Default |
| --- | --- |
| `STARTUP_DELAY_SECONDS` | `60.0` seconds for PIR stabilization |
| `INACTIVITY_TIMEOUT_SECONDS` | `120.0` seconds (two minutes) |
| `MQTT_BROKER` / `MQTT_PORT` | `10.10.0.175` / `1883` |
| `MQTT_TOPIC` | `hauntedporch/control` |
| `NEW_VISITOR_MESSAGE` | `HP_new_visitor` |
| `VISITORS_GONE_MESSAGE` | `HP_theyre_gone` |

After warm-up, the script polls every 0.2 seconds:

1. The first HIGH reading publishes `HP_new_visitor` once.
2. Further HIGH readings refresh the inactivity timer without repeating the
   arrival message. This works with either PIR jumper mode.
3. Once two minutes have passed since the last observed HIGH, a LOW reading
   causes one `HP_theyre_gone` message.
4. The next HIGH begins a new visitor session.

No departure message is sent during initial idle time or simply because the
script stops. A departure means **no PIR activity for the configured time**,
not proof that the porch is empty: stationary people can go undetected.
New arrivals during an active session extend it rather than publish another
arrival.

Messages use QoS 1 and are **not retained**, so new subscribers do not replay
old triggers. Publication is logged only after broker acknowledgement; QoS 1
can deliver duplicates, so subscribers should tolerate them. Connection and
publish acknowledgements have a ten-second timeout. MQTT/GPIO errors surface
and stop the script rather than silently dropping events. Paho's background
network loop handles ordinary reconnects, but a failed/timed-out publication
still stops the script.

Ctrl+C disconnects MQTT, stops its network loop, and releases only GPIO 6.
Do not run this monitor and the raw PIR test simultaneously.

Hardware-free tests for both scripts:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```