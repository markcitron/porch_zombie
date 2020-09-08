#!/usr/bin/python3

# import servo_controls
from cli import CLI

def main():
    """ Porch Zombie!!! 
        """
    # Start CLI
    zom_con = CLI("Porch Zombie Control")
    zom_con.display_status()
    while True:
        zom_con.get_input()

if __name__ == "__main__":
    main()