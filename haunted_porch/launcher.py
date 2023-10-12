#!/usr/bin/python3

import argparse

def make_parser():
    """ Create an argument parser """
    p = argparse.ArgumentParser(description="")
    p.add_argument("--action", "-a", help="Start or stop the Haunted Porch. Expects start|stop")
    return p

def check_args(args):
    """ eval passed arguments """
    allowable_vlaues = ["start", "stop"]
    while args.action not in allowable_vlaues:
        args.action = input(" | Missing requrie param: action. Valid options are 'start|stop', Action=? ")
        if args.action not in allowable_vlaues:
            args.action = ""
        return args

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
    shoudRun = True
    while shoudRun:
        # do something

        # case for breaking loop
        # if ______:
            # shouldRun = False

        pass


if __name__ == "__main__":
    main()
