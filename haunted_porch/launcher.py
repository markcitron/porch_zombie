#!/usr/bin/python3

import argparse
from gpiozero import MotionSensor
from signal import pause
import time

def make_parser():
    """ Create an argument parser """
    p = argparse.ArgumentParser(description="")
    p.add_argument("--action", "-a", help="Start or stop the Haunted Porch. Expects start|stop")
    return p

def check_args(args):
    """ eval passed arguments """
    allowable_vlaues = ["auto", "remote"]
    while args.action not in allowable_vlaues:
        args.action = input(" | Missing requrie param: action. Valid options are 'auto|remote', Action=? ")
        if args.action not in allowable_vlaues:
            args.action = ""
        return args

def someone_is_here():
    print("-------------------------------Motion detected------------------------------")
    time.sleep(1)
    return True

def main():
    # Intro
    print("-------------------------------------------------")
    print("              Haunted Porch")
    print("-------------------------------------------------")

    # passed arguments
    passed_args = make_parser().parse_args()
    args = check_args(passed_args)
    print("  | Going to {0} the Haunted Porch".format(args.action))

    # start things up 
    pir = MotionSensor(18) # bind motion sensor to GPIO pin 18
    while args.action == "auto":
        pir.when_motion = someone_is_here
        time.sleep(1)

    # if no motion
    # pir.when_no_motion = no_motion_function

if __name__ == "__main__":
    main()

