#!/usr/bin/python3

import tailer, os, time, threading

def wrapped_wget(url):
    """ wgets passed url
            expects url
            returns status (boolean), status message"""
    cmd = "wget -O/dev/null -q {0}".format(url)
    try: 
        os.system(cmd) 
    except Exception as e:
        print("Encountered error: {}".format(e))

def main():
    motion_log = "/var/log/motion/motion.log"
    start_trigger = "Motion detected - starting event"
    end_trigger = "End of event"
    call_status = True
    call_message = ""
    for line in tailer.follow(open(motion_log)):
        if start_trigger in line:
            print("Motion detected.")
            # Wake up Zombie1
            zombie_thread1 = threading.Thread(target=wrapped_wget, args=("http://10.10.0.3:5000/wake/",))
            # Move Spider back and forth
            # Start moving hands movers
            zombie_thread1.start()
            zombie_thread1.join()

            time.sleep(30)
        if end_trigger in line:
            print("No more motion.")
            # Go to sleep Zombie1
            zombie_thread1 = threading.Thread(target=wrapped_wget, args=("http://10.10.0.3:5000/sleep/",))
            zombie_thread1.start()
            zombie_thread1.join()
            time.sleep(60)

if __name__ == "__main__":
    main()


