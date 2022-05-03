#!/usr/bin/python3

import sys, time
from servo_controls import *
from sh import tail

def main():
    motion_log = "/var/log/motion/motion.log"
    for line in tail("-f", motion_log, _iter=True):
        if "motion_detected" in line: 
            lrap() 
            time.sleep(5) 
            blrap()
            time.sleep(30)

if __name__ == "__main__":
    main()
