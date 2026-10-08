#!/usr/bin/python3
"""Interactively test the scarecrow's articulated hands."""

from typing import Dict, Tuple

from scarecrow_actions import (
    HandController,
    HandName,
    HandPose,
    initialize_hardware,
)

MENU_ACTIONS: Dict[str, Tuple[HandName, HandPose]] = {
    "1": (HandName.LEFT, HandPose.OPEN),
    "2": (HandName.LEFT, HandPose.CLOSED),
    "3": (HandName.RIGHT, HandPose.OPEN),
    "4": (HandName.RIGHT, HandPose.CLOSED),
}


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
