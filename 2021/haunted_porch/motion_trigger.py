#!/usr/bin/python3

import tailer, os, time

def wrapped_wget(url):
    """ wgets passed url
            expects url
            returns status (boolean), status message"""
    cmd = "wget -O/dev/null -q {0}".format(url)
    try: 
        os.system(cmd) 
        return(True, "Everything is good")
    except Exception as e:
        return(False, e)

def main():
    motion_log = "/var/log/motion/motion.log"
    start_trigger = "Motion detected - starting event"
    end_trigger = "End of event"
    for line in tailer.follow(open(motion_log)):
        if start_trigger in line:
            print("Motion detected.")
            call_status, call_message = wrapped_wget("http://10.10.0.3:5000/wake/")
            time.sleep(30)
        if end_trigger in line:
            print("No more motion.")
            call_status, call_message = wrapped_wget("http://10.10.0.3:5000/sleep/")
            time.sleep(30)
        if not call_status:
            print("Encountered error: ".format(call_message))

if __name__ == "__main__":
    main()


