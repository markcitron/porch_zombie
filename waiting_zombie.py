#!/usr/bin/python3

import sys, time, random
from servo_controls import *
from sh import tail

def zombie_motion():
    motions = [no_dont_think_so]
    selected_motion = random.randint(0,len(motions))
    try: 
        motions[selected_motion]()
    except Exception as e:
        print("Error: unable to do random motion")
        print("       Exception: {0}".format(e))
    return True

def main():
    # log file
    motion_log = "/var/log/motion/motion.log"

    # counter for random motions
    seconds = 0

    for line in tail("-f", motion_log, _iter=True): 
        if "motion_detected" in line: 
            lrap() 
            time.sleep(5) 
            blrap()
            time.sleep(30)

        # do a check and if rights chance do some creepy moves :-)
        if seconds == 10:
            if random.randint(0,9) == 1:
                zombie_motion()
            seconds = 0
        else:
            seconds += 1

        time.sleep(1)


if __name__ == "__main__":
    main()
