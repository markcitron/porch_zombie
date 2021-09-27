#!/usr/bin/python3

import tailer

def main():
    motion_log = "/var/log/motion/motion.log"
    start_trigger = "Motion detected - starting event"
    end_trigger = "End of event"
    for line in tailer.follow(open(motion_log)):
        if start_trigger in line:
            print("Motion detected.")
        if end_trigger in line:
            print("No more motion.")

if __name__ == "__main__":
    main()


