#!/usr/bin/python3
"""Run a combined arm-and-hand scarecrow action."""

import argparse
import time
from typing import List, Optional

from scarecrow_actions import (
    HandController,
    WristController,
    WristName,
    WristPose,
    close_arms,
    close_hands,
    initialize_hardware,
    open_arms,
    open_hands,
    set_wrist_pose,
)

HAND_DELAY_SECONDS = 0.5


def grab(
    hand_controller: HandController,
    wrist_controller: WristController,
    hand_delay: float = HAND_DELAY_SECONDS,
) -> None:
    close_arms()
    time.sleep(hand_delay)
    set_wrist_pose(
        wrist_controller,
        WristName.LEFT,
        WristPose.PALM_FORWARD,
    )
    set_wrist_pose(
        wrist_controller,
        WristName.RIGHT,
        WristPose.PALM_FORWARD,
    )
    time.sleep(hand_delay)
    close_hands(hand_controller)


def let_go(
    hand_controller: HandController,
    wrist_controller: WristController,
    hand_delay: float = HAND_DELAY_SECONDS,
) -> None:
    open_arms()
    time.sleep(hand_delay)
    set_wrist_pose(wrist_controller, WristName.LEFT, WristPose.PALM_UP)
    set_wrist_pose(wrist_controller, WristName.RIGHT, WristPose.PALM_UP)
    time.sleep(hand_delay)
    open_hands(hand_controller)


def parse_action(arguments: Optional[List[str]] = None) -> str:
    parser = argparse.ArgumentParser(
        description="Test a combined scarecrow action."
    )
    parser.add_argument(
        "action",
        nargs="+",
        help='Action to run: "grab" or "let go"',
    )
    parsed = parser.parse_args(arguments)
    action = " ".join(parsed.action).lower()
    if action not in ("grab", "let go"):
        parser.error('action must be "grab" or "let go"')
    return action


def main() -> None:
    action = parse_action()
    initialize_hardware()
    hand_controller = HandController()
    wrist_controller = WristController()

    if action == "grab":
        grab(hand_controller, wrist_controller)
    else:
        let_go(hand_controller, wrist_controller)


if __name__ == "__main__":
    main()
