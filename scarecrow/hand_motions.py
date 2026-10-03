#!/usr/bin/python3
"""Control and interactively test the scarecrow's articulated hands."""

from dataclasses import dataclass
from enum import Enum
from time import sleep
from typing import Callable, Dict, Tuple

from robot_hat import Servo
from robot_hat.utils import reset_mcu


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

MENU_ACTIONS: Dict[str, Tuple[HandName, HandPose]] = {
    "1": (HandName.LEFT, HandPose.OPEN),
    "2": (HandName.LEFT, HandPose.CLOSED),
    "3": (HandName.RIGHT, HandPose.OPEN),
    "4": (HandName.RIGHT, HandPose.CLOSED),
}


def initialize_hardware() -> None:
    """Reset the controller before creating or moving any servos."""
    reset_mcu()
    sleep(1)


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
        action = "opening" if pose is HandPose.OPEN else "closing"
        print(f"{action} {hand.value} hand")

        for finger, config in HAND_CONFIG[hand].items():
            angle = (
                config.open_angle
                if pose is HandPose.OPEN
                else config.closed_angle
            )
            self._servos[hand][finger].angle(angle)


def run_interactive_test(controller: HandController) -> None:
    while True:
        print("Haunted Porch - Scarecrow")
        print("-------------------------")
        print("Testing hands")
        print("|")
        print("| 1. open left hand")
        print("| 2. close left hand")
        print("| 3. open right hand")
        print("| 4. close right hand")
        print("|")

        choice = input("|-> ? ").strip().lower()
        if choice == "q":
            print("Thanks for playing :-)")
            return

        action = MENU_ACTIONS.get(choice)
        if action is None:
            print("Unknown selection")
            continue

        hand, pose = action
        controller.set_pose(hand, pose)


def main() -> None:
    initialize_hardware()
    run_interactive_test(HandController())


if __name__ == "__main__":
    main()
