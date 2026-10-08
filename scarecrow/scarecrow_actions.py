#!/usr/bin/python3
"""Shared controls for the scarecrow's arms and articulated hands."""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List

import lib8relind
from robot_hat import Servo
from robot_hat.utils import reset_mcu

from relays import LinAct


class HandName(str, Enum):
    LEFT = "left"
    RIGHT = "right"


class HandPose(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class FingerName(str, Enum):
    THUMB = "thumb"
    INDEX = "index"
    MIDDLE = "middle"
    RING = "ring"
    PINKIE = "pinkie"


@dataclass(frozen=True)
class FingerConfig:
    channel: int
    open_angle: int
    closed_angle: int


HandConfig = Dict[FingerName, FingerConfig]
ServoFactory = Callable[[int], Servo]

HAND_CONFIG: Dict[HandName, HandConfig] = {
    HandName.LEFT: {
        FingerName.THUMB: FingerConfig(10, 90, -90),
        FingerName.INDEX: FingerConfig(8, -90, 90),
        FingerName.MIDDLE: FingerConfig(7, -90, 90),
        FingerName.RING: FingerConfig(9, -90, 90),
        FingerName.PINKIE: FingerConfig(6, -90, 90),
    },
    HandName.RIGHT: {
        FingerName.THUMB: FingerConfig(3, -90, 90),
        FingerName.INDEX: FingerConfig(0, 90, -90),
        FingerName.MIDDLE: FingerConfig(2, 90, -90),
        FingerName.RING: FingerConfig(1, 90, -90),
        FingerName.PINKIE: FingerConfig(4, 90, -90),
    },
}

RELAYS: List[LinAct] = [LinAct("", relay_id) for relay_id in range(1, 9)]

LEFT_SHOULDER_RELAY = RELAYS[0]  # Relay 1
RIGHT_SHOULDER_RELAY = RELAYS[1]  # Relay 2
RIGHT_ARM_RELAY = RELAYS[3]  # Relay 4
JAW_CONTROL_RELAY = RELAYS[4]  # Relay 5
BASE_MOVER_RELAY = RELAYS[5]  # Relay 6
LEFT_ARM_RELAY = RELAYS[6]  # Relay 7


def initialize_hardware() -> None:
    """Reset the controller before creating or moving any servos."""
    reset_mcu()
    time.sleep(1)


class HandController:
    def __init__(self, servo_factory: ServoFactory = Servo) -> None:
        self._servos: Dict[HandName, Dict[FingerName, Servo]] = {
            hand: {
                finger: servo_factory(config.channel)
                for finger, config in fingers.items()
            }
            for hand, fingers in HAND_CONFIG.items()
        }

    def set_pose(self, hand: HandName, pose: HandPose) -> None:
        """Move every finger on a hand to the requested pose."""
        action = "Opening" if pose is HandPose.OPEN else "Closing"
        print(f"{action} {hand.value} hand...")

        for finger, config in HAND_CONFIG[hand].items():
            angle = (
                config.open_angle
                if pose is HandPose.OPEN
                else config.closed_angle
            )
            self._servos[hand][finger].angle(angle)


def open_hand(controller: HandController, hand: HandName) -> None:
    controller.set_pose(hand, HandPose.OPEN)


def close_hand(controller: HandController, hand: HandName) -> None:
    controller.set_pose(hand, HandPose.CLOSED)


def open_hands(controller: HandController) -> None:
    for hand in HandName:
        open_hand(controller, hand)


def close_hands(controller: HandController) -> None:
    for hand in HandName:
        close_hand(controller, hand)


def read_relay_state(relay_num: int) -> int:
    state = lib8relind.get(0, relay_num)
    state_name = "contract (1)" if state == 1 else "extend (0)"
    print(f"Controller readback for relay {relay_num}: {state_name}")
    return state


def read_all_relay_states() -> List[int]:
    states = [lib8relind.get(0, relay_num) for relay_num in range(1, 9)]
    print(
        "Controller readback: "
        + ", ".join(
            f"{relay_num}={state}"
            for relay_num, state in enumerate(states, start=1)
        )
    )
    return states


def extend_all_relays() -> bool:
    for relay in RELAYS:
        relay.extend()
    read_all_relay_states()
    return True


def contract_all_relays() -> bool:
    for relay in RELAYS:
        relay.contract()
    read_all_relay_states()
    return True


def close_arms() -> bool:
    print("Closing arms...")
    LEFT_SHOULDER_RELAY.extend()
    RIGHT_SHOULDER_RELAY.extend()
    RIGHT_ARM_RELAY.contract()
    LEFT_ARM_RELAY.contract()
    JAW_CONTROL_RELAY.extend()
    return True


def open_arms() -> bool:
    print("Opening arms...")
    LEFT_SHOULDER_RELAY.contract()
    RIGHT_SHOULDER_RELAY.contract()
    RIGHT_ARM_RELAY.extend()
    LEFT_ARM_RELAY.extend()
    JAW_CONTROL_RELAY.contract()
    return True


def contract_then_extend_relay(
    relay_num: int,
    contract_time: float = 1,
    extend_time: float = 1,
) -> bool:
    if not 1 <= relay_num <= len(RELAYS):
        print("Invalid relay number. Must be 1-8.")
        return False

    relay = RELAYS[relay_num - 1]
    print(f"Contracting relay {relay_num}...")
    relay.contract()
    read_relay_state(relay_num)
    time.sleep(contract_time)
    print(f"Extending relay {relay_num}...")
    relay.extend()
    read_relay_state(relay_num)
    time.sleep(extend_time)
    return True
