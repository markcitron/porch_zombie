#!/usr/bin/python3
"""Control the scarecrow base from Mad Scientist visitor events."""

from typing import List, Optional

import paho.mqtt.client as mqtt

from relays import LinAct

MQTT_BROKER = "10.10.0.175"
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
NEW_VISITOR_MESSAGE = "HP_new_visitor"
VISITORS_GONE_MESSAGE = "HP_theyre_gone"

BASE_RELAY = LinAct("Scarecrow base", 6)


def on_connect(
    client: mqtt.Client,
    _userdata: object,
    _flags: mqtt.ConnectFlags,
    reason_code: mqtt.ReasonCode,
    _properties: Optional[mqtt.Properties],
) -> None:
    if reason_code.is_failure:
        raise ConnectionError(f"MQTT connection rejected: {reason_code}")
    result, _mid = client.subscribe(MQTT_TOPIC, qos=1)
    if result != mqtt.MQTT_ERR_SUCCESS:
        raise RuntimeError(f"MQTT subscription failed with code {result}")
    print(
        f"Connected to {MQTT_BROKER}:{MQTT_PORT}; "
        f"requesting subscription to {MQTT_TOPIC}.",
        flush=True,
    )


def on_subscribe(
    _client: mqtt.Client,
    _userdata: object,
    _mid: int,
    reason_codes: List[mqtt.ReasonCode],
    _properties: Optional[mqtt.Properties],
) -> None:
    if not reason_codes or any(code.is_failure for code in reason_codes):
        raise RuntimeError(f"MQTT subscription rejected: {reason_codes}")
    print(f"Listening for visitor events on {MQTT_TOPIC}.", flush=True)


def on_disconnect(
    _client: mqtt.Client,
    _userdata: object,
    _flags: mqtt.DisconnectFlags,
    reason_code: mqtt.ReasonCode,
    _properties: Optional[mqtt.Properties],
) -> None:
    if reason_code.is_failure:
        print(
            f"MQTT connection lost: {reason_code}. Keeping relay 6 unchanged "
            "while reconnecting.",
            flush=True,
        )
    else:
        print("MQTT disconnected; relay 6 unchanged by disconnect.", flush=True)


def on_message(
    _client: mqtt.Client,
    _userdata: object,
    message: mqtt.MQTTMessage,
) -> None:
    if message.topic != MQTT_TOPIC:
        print(f"Ignoring message on unexpected topic {message.topic!r}.", flush=True)
        return
    if message.retain:
        print(f"Ignoring retained visitor event: {message.payload!r}.", flush=True)
        return
    try:
        payload = message.payload.decode("utf-8")
    except UnicodeDecodeError:
        print(f"Ignoring non-UTF-8 MQTT payload: {message.payload!r}.", flush=True)
        return

    if payload == NEW_VISITOR_MESSAGE:
        BASE_RELAY.extend()
        print("HP_new_visitor: relay 6 extended (1).", flush=True)
    elif payload == VISITORS_GONE_MESSAGE:
        BASE_RELAY.contract()
        print("HP_theyre_gone: relay 6 contracted (0).", flush=True)
    else:
        print(f"Ignoring unrelated MQTT payload: {payload!r}.", flush=True)


def main() -> None:
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        protocol=mqtt.MQTTv311,
    )
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    try:
        BASE_RELAY.contract()
        print("Relay 6 contracted (0). Connecting to MQTT; Ctrl+C to stop.", flush=True)
        result = client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        if result != mqtt.MQTT_ERR_SUCCESS:
            raise ConnectionError(f"MQTT connect failed with code {result}")
        result = client.loop_forever()
        if result != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT network loop exited with code {result}")
    except KeyboardInterrupt:
        print("\nStopping scarecrow listener.", flush=True)
    finally:
        try:
            BASE_RELAY.contract()
            print("Relay 6 contracted (0) for shutdown.", flush=True)
        finally:
            client.disconnect()


if __name__ == "__main__":
    main()