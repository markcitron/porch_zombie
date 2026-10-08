#!/usr/bin/python3

from scarecrow_actions import (
    close_arms,
    contract_all_relays,
    contract_then_extend_relay,
    extend_all_relays,
    open_arms,
    read_all_relay_states,
)


def main():
    while True:
        print("\nRelay Test Menu:")
        print("1: Extend all relays")
        print("2: Contract all relays")
        print("3: Contract then extend a single relay")
        print("4: Read controller state for all relays")
        print("5: Open arms")
        print("6: Close arms")
        print("q: Quit")
        choice = str(input("Select test to run: "))
        if choice == '1':
            extend_all_relays()
        elif choice == '2':
            contract_all_relays()
        elif choice == '3':
            try:
                relay_num = int(input("Enter relay number (1-8): "))
                contract_then_extend_relay(relay_num)
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 8.")
        elif choice == '4':
            read_all_relay_states()
        elif choice == '5':
            open_arms()
        elif choice == '6':
            close_arms()
        elif choice == 'q':
            print("Exiting relay test.")
            break
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main()
