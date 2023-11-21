#!/usr/bin/python3

import tailer

looking_for = ["motion_detected","End of event"]
for line in tailer.follow(open('/var/log/motion/motion.log')):
    if "motion_detected" in line:
        print("Motion detected: {}".format(line))
    elif "End of event" in line:
        print("No more motion: {}".format(line))

