#!/usr/bin/python3
"""
Main production day trigger script.
- Uses a PIR motion sensor on GPIO17 to detect motion.
- When motion is detected it publishes a sequence of MQTT messages to trigger each Pi bot.
- Device trigger names come from the Haunted Porch controller UI: coffin_skeleton, creepy_skull, crypt_keeper, scarecrow, electro_closet, tilting_alien

Usage: run on your main trigger Pi:
  python3 mqtt_main_trigger.py

"""
import time
import threading
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import paho.mqtt.client as mqtt

try:
    from gpiozero import MotionSensor
except Exception:
    MotionSensor = None

# Configuration
MQTT_BROKER = "10.10.0.175"
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
PIR_PIN = 23 
COOLDOWN_SECONDS = 30  # time to ignore new triggers after a sequence starts

# Sequence of triggers with per-trigger delay configuration.
# Each entry is a tuple: (device_name, delay_after_seconds)
# delay_after_seconds specifies how long to wait AFTER publishing this trigger
# before publishing the next one.
TRIGGER_SEQUENCE = [
    ("coffin_skeleton", 1.5),
    ("creepy_skull", 0.5),
    ("crypt_keeper", 1.0),
    ("scarecrow", 0.8),
    ("electro_closet", 1.2),
    ("tilting_alien", 0.5),
]

def get_trigger_sequence():
    """Return the trigger sequence. Modify this function or the TRIGGER_SEQUENCE
    definition above to customize order and delays.
    """
    # Try to load from external JSON config first
    seq = load_trigger_sequence_from_file()
    if seq:
        logger.info(f"Loaded trigger sequence from {CONFIG_FILE}")
        return seq
    return TRIGGER_SEQUENCE


CONFIG_FILE = Path(__file__).parent / "trigger_sequence.json"
LOG_FILE = Path(__file__).parent / "trigger_status.log"

def setup_logging():
    logger = logging.getLogger("porch_trigger")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2000000, backupCount=3)
    fmt = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    # also log to console
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger


def load_trigger_sequence_from_file():
    if not CONFIG_FILE.exists():
        return None
    try:
        with open(CONFIG_FILE, "r") as fh:
            cfg = json.load(fh)
        seq = []
        for entry in cfg.get("sequence", []):
            device = entry.get("device")
            delay = float(entry.get("delay_after", 0))
            seq.append((device, delay))
        return seq
    except Exception as e:
        print(f"Error loading config {CONFIG_FILE}: {e}")
        return None

# MQTT client
client = mqtt.Client(protocol=mqtt.MQTTv311)


def connect_broker():
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        return True
    except Exception as e:
        print(f"Failed to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}: {e}")
        return False


def publish_trigger(device):
    try:
        logger.info(f"Publishing trigger: {device}")
        result = client.publish(MQTT_TOPIC, device)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"Publish returned rc={result.rc}. Attempting reconnect and republish.")
            logger.warning(f"Publish returned rc={result.rc}. Attempting reconnect and republish.")
            client.reconnect()
            client.publish(MQTT_TOPIC, device)
    except Exception as e:
        logger.exception(f"Error publishing {device}: {e}")


logger = setup_logging()

# Motion handling
last_trigger_time = 0
lock = threading.Lock()


def handle_motion():
    global last_trigger_time
    with lock:
        now = time.time()
        if now - last_trigger_time < COOLDOWN_SECONDS:
            print("In cooldown window, ignoring motion.")
            return
        last_trigger_time = now

    logger.info("Motion detected: starting trigger sequence")
    # Publish triggers in their order, staggered with per-trigger delays
    seq = get_trigger_sequence()
    for device, delay_after in seq:
        publish_trigger(device)
        if delay_after and delay_after > 0:
            logger.info(f"Waiting {delay_after}s before next trigger")
            time.sleep(delay_after)

    logger.info("Trigger sequence complete. Entering cooldown.")


def pir_loop():
    if MotionSensor is None:
        logger.error("gpiozero MotionSensor not available. Exiting.")
        return

    pir = MotionSensor(PIR_PIN)
    logger.info(f"PIR sensor initialized on GPIO{PIR_PIN}. Waiting for motion...")
    while True:
        pir.wait_for_motion()
        # handle motion in a background thread so sensor loop can continue quickly
        threading.Thread(target=handle_motion).start()
        # small sleep to avoid busy loop
        time.sleep(0.1)


def main():
    connected = connect_broker()
    if not connected:
        logger.warning("Continuing without MQTT connection. Will attempt publishes which may fail.")

    if MotionSensor is None:
        logger.error("gpiozero is not installed. Install it with: sudo apt install python3-gpiozero")
        # fallback: simple loop - poll input from sysfs (not implemented)
        return

    try:
        pir_loop()
    except KeyboardInterrupt:
        print("Exiting on keyboard interrupt")
    finally:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass


if __name__ == '__main__':
    main()
