#!/usr/bin/python3

import argparse, psutil, subprocess

def make_parser():
    """ Create an argument parser """
    p = argparse.ArgumentParser(description="Starts up our Haunted Porch 2022")
    p.add_argument("--action", "-a", help="Start or stop the Haunted Porch.  Expects 'start|stop'")
    return p

def check_args(args):
    """ eval passed arguments """
    # check 'action'
    allowable_values = ["start","stop"]
    while args.action not in allowable_values:
        args.action = input("  | Missing require param: action. Valid options are 'start|stop'. Action=? ")
        if args.action not in allowable_values:
            args.action == ""
    return args

def start_script(script_name):
    try: 
        print("  | starting {0}".format(script_name))
        current_path = "/home/pi/my_repos/porch_zombie/2022/zombie0_controller/"
        command_to_run = "screen -dm {0}{1}".format(current_path, script_name)
        print(command_to_run)
        # subprocess.Popen(command_to_run, shell=False) 
        return True
    except:
        print("  | ERROR: unable to start {0}".format(script_name))
        return False

def main():
    # intro
    print("----------------------------------------------")
    print("           Haunted Porch 2022")
    print("----------------------------------------------")

    # passed arguments
    passed_args = make_parser().parse_args()
    args = check_args(passed_args)
    print("  | {0}ing the Haunted Porch".format(args.action))

    # start things up
    scripts_to_run = ["main.py", "motion_detection.py"]
    for each_script in scripts_to_run:
        if not start_script(each_script):
            # do something if unable to start needed script
            print("  | .. Failure")
        else:
            print("  | .. Success")

if __name__ == "__main__":
    main()
