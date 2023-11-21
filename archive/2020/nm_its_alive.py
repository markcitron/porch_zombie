#!/usr/bin/python3

from playsound import playsound
import sys, time, random, threading
from servo_controls import *
from sh import tail

class Thread(threading.Thread):
    def __init__(self, t, *args):
        threading.Thread.__init__(self, target=t, args=args)
        self.start()

def zombie_auto_motion():
    """" Zombie autonomouse motions - motions triggered based random pick
         at intervals 
        """
    print("Running zombie auto motion")
    check_interval = 15 # check every 10 seconds
    motion_chance = 50  # 10% change of triggering auto motion
    seconds = 0 
    while True:
        if seconds == check_interval:
            if random.random()*50 < motion_chance:
                    try: 
                        # determine motion
                        if random.random()*100 < 50:
                            no_dont_think_so()
                        else:
                            motion_motion()
                    except Exception as e: 
                        print("Error: Unable to do random motion") 
                        print("Exception: {0}".format(e))
            else:
                print("missed the check and not running anything")
            seconds = 0
        else: 
            seconds += 1
        time.sleep(1)

def main():
    #zombie_auto_motion()
    while True:
        no_dont_think_so()
        time.sleep(10)

if __name__ == "__main__":
    main()

