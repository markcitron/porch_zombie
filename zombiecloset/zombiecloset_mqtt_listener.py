#!/usr/bin/python3
"""Run a delayed Zombie Closet sequence for each MQTT visitor session."""

from __future__ import annotations

import math
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from typing import Deque, List, Optional, Tuple

import paho.mqtt.client as mqtt

from relays import gpio_cleanup
from zombie_closet import activate_sidekick, activate_zc, close_closet

MQTT_BROKER = "10.10.0.175"
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
NEW_VISITOR_MESSAGE = "HP_new_visitor"
VISITORS_GONE_MESSAGE = "HP_theyre_gone"

VISITOR_DELAY_SECONDS = 10.0
POLL_INTERVAL_SECONDS = 0.2

VisitorEvent = Tuple[str, float]


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
            f"MQTT connection lost: {reason_code}. Reconnecting; "
            "pending sequences remain scheduled.",
            flush=True,
        )
    else:
        print("MQTT disconnected.", flush=True)


def on_message(
    _client: mqtt.Client,
    userdata: object,
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
    if payload not in (NEW_VISITOR_MESSAGE, VISITORS_GONE_MESSAGE):
        print(f"Ignoring unrelated MQTT payload: {payload!r}.", flush=True)
        return
    if not isinstance(userdata, Queue):
        raise TypeError("MQTT userdata must be the visitor event queue")
    userdata.put((payload, time.monotonic()))
    print(f"Queued visitor event: {payload}.", flush=True)


def run_visitor_sequence() -> None:
    activate_sidekick()
    time.sleep(5)
    activate_zc()
    time.sleep(30)
    activate_sidekick()


class VisitorController:
    def __init__(self, events: Queue[VisitorEvent]) -> None:
        self.events = events
        self.session_active = False
        self.pending: Deque[float] = deque()

    def update(self) -> None:
        while True:
            try:
                event, received_at = self.events.get_nowait()
            except Empty:
                break
            if event == NEW_VISITOR_MESSAGE:
                if not self.session_active:
                    self.session_active = True
                    self.pending.append(received_at + VISITOR_DELAY_SECONDS)
                    print(
                        f"Visitor sequence scheduled after "
                        f"{VISITOR_DELAY_SECONDS:g} seconds.",
                        flush=True,
                    )
            elif event == VISITORS_GONE_MESSAGE:
                self.session_active = False
                print(
                    "Visitor session ended; pending activations are unchanged.",
                    flush=True,
                )
            else:
                raise ValueError(f"Unexpected queued visitor event: {event!r}")

        if self.pending and time.monotonic() >= self.pending[0]:
            self.pending.popleft()
            print("Starting Zombie Closet visitor sequence.", flush=True)
            run_visitor_sequence()
            print("Zombie Closet visitor sequence complete.", flush=True)


def run_controller(client: mqtt.Client, controller: VisitorController) -> None:
    with ThreadPoolExecutor(max_workers=1) as executor:
        network = executor.submit(client.loop_forever)
        try:
            while not network.done():
                controller.update()
                time.sleep(POLL_INTERVAL_SECONDS)
        finally:
            client.disconnect()
            result = network.result()
            if result != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"MQTT network loop exited with code {result}")


def main() -> None:
    if not math.isfinite(VISITOR_DELAY_SECONDS) or VISITOR_DELAY_SECONDS < 0:
        raise ValueError("VISITOR_DELAY_SECONDS must be finite and nonnegative")
    if not math.isfinite(POLL_INTERVAL_SECONDS) or POLL_INTERVAL_SECONDS <= 0:
        raise ValueError("POLL_INTERVAL_SECONDS must be finite and positive")
    events: Queue[VisitorEvent] = Queue()
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        protocol=mqtt.MQTTv311,
        userdata=events,
    )
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    try:
        close_closet()
        result = client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        if result != mqtt.MQTT_ERR_SUCCESS:
            raise ConnectionError(f"MQTT connect failed with code {result}")
        run_controller(client, VisitorController(events))
    except KeyboardInterrupt:
        print("\nStopping Zombie Closet listener.", flush=True)
    finally:
        try:
            close_closet()
        finally:
            try:
                gpio_cleanup()
            finally:
                client.disconnect()


if __name__ == "__main__":
    main()