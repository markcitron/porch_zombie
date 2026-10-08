#!/usr/bin/python3
"""Run a combined arm-and-hand scarecrow action."""

import argparse
import time
from typing import List, Optional

from scarecrow_actions import (
    HandController,
    close_arms,
    close_hands,
    initialize_hardware,
    open_arms,
    open_hands,
)

HAND_DELAY_SECONDS = 0.5


def grab(
    controller: HandController,
    hand_delay: float = HAND_DELAY_SECONDS,
) -> None:
    close_arms()
    time.sleep(hand_delay)
    close_hands(controller)


def let_go(
    controller: HandController,
    hand_delay: float = HAND_DELAY_SECONDS,
) -> None:
    open_arms()
    time.sleep(hand_delay)
    open_hands(controller)


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
    controller = HandController()

    if action == "grab":
        grab(controller)
    else:
        let_go(controller)


if __name__ == "__main__":
    main()
