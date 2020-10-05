#!/usr/bin/python3

import sys, time
from servo_controls import *
from sh import tail

def zombie_motion():
    return which_motion()

def main():
    # log file
    motion_log = "/var/log/motion/motion.log"

    # state variable
    zombie_in_motion = False

    for line in tail("-f", motion_log, _iter=True):
        # if the zombie isn't in motion, move if someone triggers it
        if not zombie_in_motion:
            if "motion_detected" in line: 
                zombie_in_motion = True
                lrap() 
                time.sleep(5) 
                blrap()
                time.sleep(30)
            zombie_in_motion = False

        # do a check and if rights chance do some creepy moves :-)

if __name__ == "__main__":
    main()
