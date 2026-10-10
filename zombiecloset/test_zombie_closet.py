#!/usr/bin/python3
"""Interactively test the Zombie Closet."""

from relays import gpio_cleanup
from zombie_closet import activate_zc, close_closet, open_closet, activate_sidekick


def main():
    try:
        while True:
            print("\nZombie Closet Test Menu:")
            print("1: Open the closet")
            print("2: Close the closet")
            print("3: Activate the closet")
            print("4: Activate the Sidekick")
            print("q: Quit")

            choice = input("Select test to run: ").strip().lower()
            if choice == "1":
                open_closet()
            elif choice == "2":
                close_closet()
            elif choice == "3":
                activate_zc()
            elif choice == "4":
                activate_sidekick()
            elif choice == "q":
                print("Exiting Zombie Closet test.")
                break
            else:
                print("Invalid selection. Please choose 1, 2, 3, 4, or q.")
    finally:
        close_closet()
        gpio_cleanup()


if __name__ == "__main__":
    main()
