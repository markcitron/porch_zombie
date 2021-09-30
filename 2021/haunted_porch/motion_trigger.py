#!/usr/bin/python3

import tailer, os, time

def wrapped_get(url):
    cmd = "wget -qO {0} &> /dev/null".format(url)
    try: 
        os.system(cmd) 
        return True
    except:
        return False

def main():
    motion_log = "/var/log/motion/motion.log"
    start_trigger = "Motion detected - starting event"
    end_trigger = "End of event"
    for line in tailer.follow(open(motion_log)):
        if start_trigger in line:
            print("Motion detected.")
            wrapped_get("http://10.10.0.3:5000/wake/")
            time.sleep(30)
        if end_trigger in line:
            print("No more motion.")
            wrapped_get("http://10.10.0.3:5000/sleep/")
            time.sleep(30)

if __name__ == "__main__":
    main()


