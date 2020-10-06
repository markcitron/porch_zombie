#!/usr/bin/python3

import sys, time, random, threading
from servo_controls import *
from sh import tail

class Thread(threading.Thread):
    def __init__(self, t, *args):
        threading.Thread.__init__(self, target=t, args=args)
        self.start()

def tail_motion_log(motion_log):
    """ function to tail the motion log and trigger when 
        motion_detected is in line.

        Takes: motion_log
        """

    for line in tail("-f", motion_log, _iter=True):
        if "motion_detected" in line:
            # only move zombie if it isn't already in motion
            # it is undead, let's not confuse it
            with threading.Lock():
                zombie_in_motion = True
                lrap()
                time.sleep(5)
                blrap()
                time.sleep(30)
                zombie_in_motion = False 

def zombie_auto_motion():
    """" Zombie autonomouse motions - motions triggered based random pick
         at intervals 
        """
    check_interval = 10 # check every 10 seconds
    motion_change = 10  # 10% change of triggering auto motion
    motions = [no_dont_think_so]
    seconds = 0 
    while True:
        if seconds == check_interval:
            if random.random()*100 < motion_chance:
                with threading.Lock():
                    zombin_in_motion = True
                    # selected_motion = random.randint(0, len(motions)) 
                    try: 
                        # motion[selected_motion]() 
                        no_dont_think_so()
                    except Exception as e: 
                        print("Error: Unable to do random motion") 
                        print("Exception: {0}".format(e))
                    zombin_in_motion = False 
        else: 
            seconds += 1
        time.sleep(1)

def main():
    motion_log = "/var/log/motion/motion.log"

    """
    t1 = threading.Thread(target=tail_motion_log, args=(motion_log,))
    t2 = threading.Thread(target=zombie_auto_motion)

    t1.start()
    t2.start()
    """

    Zombie_auto = Thread(zombie_auto_motion)
    zombie_reac = Thread(tail_motion_log, (motion_log,))

if __name__ == "__main__":
    main()

