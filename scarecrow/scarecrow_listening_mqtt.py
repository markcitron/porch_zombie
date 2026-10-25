#!/usr/bin/python3
"""Coordinate MQTT visitor events, base rotation, and distance-triggered grabs."""

from __future__ import annotations

import math
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from typing import List, Optional

import paho.mqtt.client as mqtt
from robot_hat import Pin, Ultrasonic

from relays import LinAct
from scarecrow_actions import HandController, WristController, initialize_hardware
from scarecrow_waiting import (
    HOLD_SECONDS,
    STARTUP_DELAY_SECONDS,
    TRIGGER_DISTANCE_CM,
)
from test_actions import grab, let_go
from test_distance_ultra import ECHO_PIN, READ_INTERVAL, TRIGGER_PIN

MQTT_BROKER = "10.10.0.175"
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"
NEW_VISITOR_MESSAGE = "HP_new_visitor"
VISITORS_GONE_MESSAGE = "HP_theyre_gone"
BASE_SETTLE_SECONDS = 0.0

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
    userdata.put(payload)
    print(f"Queued visitor event: {payload}.", flush=True)


class ScarecrowController:
    def __init__(
        self,
        events: Queue[str],
        ultrasonic: Ultrasonic,
        hand_controller: HandController,
        wrist_controller: WristController,
    ) -> None:
        self.events = events
        self.ultrasonic = ultrasonic
        self.hand_controller = hand_controller
        self.wrist_controller = wrist_controller
        self.active = False
        self.armed = True
        self.holding = False
        self.hold_until = 0.0
        self.startup_ready_at = time.monotonic() + STARTUP_DELAY_SECONDS
        self.ready_at = self.startup_ready_at

    def release(self) -> None:
        let_go(self.hand_controller, self.wrist_controller)
        self.holding = False

    def process_events(self) -> None:
        while True:
            try:
                event = self.events.get_nowait()
            except Empty:
                return
            if event == NEW_VISITOR_MESSAGE:
                if not self.active:
                    BASE_RELAY.extend()
                    self.active = True
                    self.armed = True
                    self.ready_at = max(
                        self.startup_ready_at,
                        time.monotonic() + BASE_SETTLE_SECONDS,
                    )
                    print("HP_new_visitor: relay 6 extended (1).", flush=True)
            elif event == VISITORS_GONE_MESSAGE:
                if self.active:
                    self.active = False
                    if self.holding:
                        self.release()
                    BASE_RELAY.contract()
                    print("HP_theyre_gone: released; relay 6 contracted (0).", flush=True)
            else:
                raise ValueError(f"Unexpected queued visitor event: {event!r}")

    def update(self) -> None:
        self.process_events()
        if not self.active or time.monotonic() < self.ready_at:
            return
        if self.holding:
            if time.monotonic() >= self.hold_until:
                self.release()
            return

        distance = self.ultrasonic.read()
        # A departure received during the sensor read must precede a new grab.
        self.process_events()
        if not self.active or time.monotonic() < self.ready_at:
            return
        if not math.isfinite(distance) or distance < 0:
            print(
                f"Invalid ultrasonic reading ({distance!r}); "
                "check sensor power and TRIG/ECHO wiring.",
                flush=True,
            )
        elif distance > TRIGGER_DISTANCE_CM:
            self.armed = True
        elif self.armed:
            self.armed = False
            self.holding = True
            print(f"Visitor at {distance:.2f} cm. Grabbing.", flush=True)
            grab(self.hand_controller, self.wrist_controller)
            self.hold_until = time.monotonic() + HOLD_SECONDS
            self.process_events()


def run_controller(client: mqtt.Client, controller: ScarecrowController) -> None:
    with ThreadPoolExecutor(max_workers=1) as executor:
        network = executor.submit(client.loop_forever)
        try:
            while not network.done():
                controller.update()
                time.sleep(READ_INTERVAL)
        finally:
            client.disconnect()
            result = network.result()
            if result != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"MQTT network loop exited with code {result}")


def validate_configuration() -> None:
    for name, value, minimum_is_valid in (
        ("TRIGGER_DISTANCE_CM", TRIGGER_DISTANCE_CM, False),
        ("READ_INTERVAL", READ_INTERVAL, False),
        ("STARTUP_DELAY_SECONDS", STARTUP_DELAY_SECONDS, True),
        ("HOLD_SECONDS", HOLD_SECONDS, True),
        ("BASE_SETTLE_SECONDS", BASE_SETTLE_SECONDS, True),
    ):
        if not math.isfinite(value) or value < 0 or (value == 0 and not minimum_is_valid):
            raise ValueError(f"Invalid {name}: {value!r}")


def main() -> None:
    validate_configuration()
    events: Queue[str] = Queue()
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        protocol=mqtt.MQTTv311,
        userdata=events,
    )
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    controller: Optional[ScarecrowController] = None
    try:
        BASE_RELAY.contract()
        initialize_hardware()
        hand_controller = HandController()
        wrist_controller = WristController()
        controller = ScarecrowController(
            events,
            Ultrasonic(Pin(TRIGGER_PIN), Pin(ECHO_PIN)),
            hand_controller,
            wrist_controller,
        )
        controller.release()
        print(
            f"Relay 6 contracted (0); waiting for visitor events. "
            f"Grabs enabled after {STARTUP_DELAY_SECONDS:g} seconds, "
            f"at {TRIGGER_DISTANCE_CM:g} cm or closer. Ctrl+C to stop.",
            flush=True,
        )
        result = client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        if result != mqtt.MQTT_ERR_SUCCESS:
            raise ConnectionError(f"MQTT connect failed with code {result}")
        run_controller(client, controller)
    except KeyboardInterrupt:
        print("\nStopping scarecrow listener.", flush=True)
    finally:
        try:
            if controller is not None:
                controller.release()
        finally:
            try:
                BASE_RELAY.contract()
                print("Relay 6 contracted (0) for shutdown.", flush=True)
            finally:
                client.disconnect()


if __name__ == "__main__":
    main()