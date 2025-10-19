#!/home/pi/repos/porch_zombie/venv/bin/python
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

# Sound playback
try:
    import pygame
except ImportError:
    pygame = None
# Sequence of triggers with per-trigger delay configuration.
# ...existing code...

# Path to spooky sound file
SPOOKY_SOUND_PATH = str(Path(__file__).parent / "sounds/spooky-halloween-effects-with-thunder-121665.mp3")

try:
    from gpiozero import MotionSensor
except Exception:
    MotionSensor = None

# Configuration
MQTT_BROKER = "10.10.0.175"
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
PIR_PIN = 23 
COOLDOWN_SECONDS = 180  # time to ignore new triggers after a sequence starts

# Sequence of triggers with per-trigger delay configuration.
# Each entry is a tuple: (device_name, delay_after_seconds)
# delay_after_seconds specifies how long to wait AFTER publishing this trigger
# before publishing the next one.
TRIGGER_SEQUENCE = [
    ("crypt_keeper_2", 1.0),
    ("scarecrow", 0.8 ),
    ("crypt_keeper_1", 1.0),
    ("electro_closet", 3.0),
    ("creepy_skull", 5),
    ("coffin_skeleton", 3.0)
]

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


    # Start playing spooky sound
    if pygame is not None:
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(SPOOKY_SOUND_PATH)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1)  # loop until stopped
            logger.info(f"Playing spooky sound: {SPOOKY_SOUND_PATH} at volume 1.0")
        except Exception as e:
            logger.warning(f"Could not play spooky sound: {e}")
    else:
        logger.warning("pygame not installed, cannot play spooky sound.")

    # Wait 1 second before starting triggers
    time.sleep(1)


    # Publish triggers in their order, staggered with per-trigger delays
    for device, delay_after in TRIGGER_SEQUENCE:
        publish_trigger(device)
        if delay_after and delay_after > 0:
            logger.info(f"Waiting {delay_after}s before next trigger")
            time.sleep(delay_after)

    time.sleep(60)

    # Stop music after triggers are done
    if pygame is not None:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.quit()
            logger.info("Spooky sound stopped.")
        except Exception as e:
            logger.warning(f"Could not stop spooky sound: {e}")

    logger.info("Trigger sequence complete. Entering cooldown.")


def pir_loop():
    if MotionSensor is None:
        logger.error("gpiozero MotionSensor not available. Exiting.")
        return

    pir = MotionSensor(PIR_PIN)
    logger.info(f"PIR sensor initialized on GPIO{PIR_PIN}. Waiting for sensor to stabilize...")
    # Startup delay to allow PIR sensor to stabilize
    STARTUP_DELAY = 30
    time.sleep(STARTUP_DELAY)
    logger.info(f"Startup delay of {STARTUP_DELAY} seconds complete. Now waiting for motion...")
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
