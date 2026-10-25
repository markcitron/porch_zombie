#!/usr/bin/python3
"""Publish porch arrival/departure events from the Mad Scientist PIR."""

import math
import time

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

PIR_PIN = 6  # BCM GPIO 6, physical header pin 31
READ_INTERVAL_SECONDS = 0.2
STARTUP_DELAY_SECONDS = 60.0
INACTIVITY_TIMEOUT_SECONDS = 120.0

MQTT_BROKER = "10.10.0.175"
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
NEW_VISITOR_MESSAGE = "HP_new_visitor"
VISITORS_GONE_MESSAGE = "HP_theyre_gone"
MQTT_TIMEOUT_SECONDS = 10.0


def connect_mqtt(client: mqtt.Client) -> None:
    result = client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    if result != mqtt.MQTT_ERR_SUCCESS:
        raise RuntimeError(f"MQTT connect failed with code {result}")
    result = client.loop_start()
    if result != mqtt.MQTT_ERR_SUCCESS:
        raise RuntimeError(f"MQTT network loop failed with code {result}")

    deadline = time.monotonic() + MQTT_TIMEOUT_SECONDS
    while not client.is_connected():
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"MQTT connection to {MQTT_BROKER}:{MQTT_PORT} "
                "was not acknowledged"
            )
        time.sleep(READ_INTERVAL_SECONDS)
    print(f"Connected to MQTT at {MQTT_BROKER}:{MQTT_PORT}.", flush=True)


def publish_event(client: mqtt.Client, message: str) -> None:
    result = client.publish(MQTT_TOPIC, payload=message, qos=1, retain=False)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        raise RuntimeError(
            f"MQTT publish of {message!r} failed with code {result.rc}"
        )
    result.wait_for_publish(timeout=MQTT_TIMEOUT_SECONDS)
    if not result.is_published():
        raise TimeoutError(f"MQTT publish of {message!r} was not acknowledged")
    print(f"Published {message} on {MQTT_TOPIC}.", flush=True)


def watch_for_visitors(client: mqtt.Client) -> None:
    visitors_present = False
    last_activity = 0.0
    print(f"Watching for visitors on BCM GPIO {PIR_PIN}.", flush=True)

    while True:
        motion = GPIO.input(PIR_PIN)
        now = time.monotonic()

        if motion:
            last_activity = now
            if not visitors_present:
                publish_event(client, NEW_VISITOR_MESSAGE)
                visitors_present = True
        elif visitors_present and now - last_activity >= INACTIVITY_TIMEOUT_SECONDS:
            publish_event(client, VISITORS_GONE_MESSAGE)
            visitors_present = False

        time.sleep(READ_INTERVAL_SECONDS)


def main() -> None:
    if (
        not math.isfinite(INACTIVITY_TIMEOUT_SECONDS)
        or INACTIVITY_TIMEOUT_SECONDS <= 0
    ):
        raise ValueError("INACTIVITY_TIMEOUT_SECONDS must be finite and positive")
    if not math.isfinite(STARTUP_DELAY_SECONDS) or STARTUP_DELAY_SECONDS < 0:
        raise ValueError("STARTUP_DELAY_SECONDS must be finite and nonnegative")

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)
    try:
        print(
            f"Allowing {STARTUP_DELAY_SECONDS:g} seconds for PIR stabilization. "
            "Press Ctrl+C to stop.",
            flush=True,
        )
        time.sleep(STARTUP_DELAY_SECONDS)
        connect_mqtt(client)
        watch_for_visitors(client)
    except KeyboardInterrupt:
        print("\nStopping visitor monitor.", flush=True)
    finally:
        try:
            client.disconnect()
        finally:
            try:
                client.loop_stop()
            finally:
                GPIO.cleanup(PIR_PIN)


if __name__ == "__main__":
    main()