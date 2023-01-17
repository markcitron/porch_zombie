#!/usr/bin/python3

import requests, time, random
from relays import *
from datetime import datetime
import lib8relind

# set up linear actuator relays
relay1 = LinAct("sc outside arm", 1)
relay2 = LinAct("sc inside arm", 2)
relay3 = LinAct("Electrocution box", 3)
relay4 = LinAct("pumpkin voice", 4)
relay5 = LinAct("hanging ghost trigger", 5)
relay6 = LinAct("", 6)
relay7 = LinAct("sc head tilt", 7)
relay8 = LinAct("sc torso twist", 8)

def get_datetime():
    return datetime.now()

def head(updown):
    try: 
        if updown == "up": 
            relay7.extend() 
        else: 
            relay7.contract()
        return True
    except Exception as e:
        print("ERROR - {0} - when trying move head {1}, encountered exception: {2}".format(get_datetime(),updown,e))
        return False

def arm(updown):
    try:
        if updown == "up":
            relay1.extend()
            relay2.extend()
        else:
            relay1.contract()
            relay2.contract()
        return True
    except Exception as e:
        print("ERROR - {0} - when moving arm {1}, encountered exception: {2}".format(get_datetime(), updown, e))
        return False

def torso(rightleft):
    try:
        if rightleft == "right":
            relay8.extend()
        else:
            relay8.contract()
        return True
    except Exception as e:
        print("ERROR - {0} - when trying to move arm {1}, encountered exception {2}".format(get_datetime(), rightleft, e))
        return False

def audio_trigger(which):
    target_relay = relay4 # default to the scarecrow
    if which == "ghost":
        target_relay = relay5
    elif which == "box":
        target_relay = relay3
    try:
        target_relay.contract()
        time.sleep(.1)
        target_relay.extend()
        time.sleep(.1)
        target_relay.contract()
        return True
    except Exception as e:
        print("ERROR - {0} - when trying to trigger {1}, encountered exception {2}".format(get_datetime(), which, e))
        return False

def ghost_cabinet(openclose):
    # zombie2 is running on 10.10.0.83
    try: 
        if openclose == "open":
            x = requests.get('http://10.10.0.83:5000/extend_all/')
        else:
            x = requests.get('http://10.10.0.83:5000/contract_all/')
        return True
    except Exception as e:
        print("ERROR - {0} - when trying to {1} the ghost cabinet, encountered exception: {2}".format(get_datetime(), openclose, e))
        return False

def check_for_motion():
    # motion detection is running on 10.10.0.148
    # need to pull data from 148, something should be running there and returning if it is seeing motion or not.
    # can probably just use the
    pass

def porch_motion(which):
    print("{0} - Running: {1}".format(get_datetime(), which))
    if which == "reset": 
        head("down") 
        torso("left") 
        arm("down") 
        ghost_cabinet("close")
    elif which == "the_works":
        ghost_cabinet("open")
        time.sleep(1)
        audio_trigger("box")
        torso("right")
        time.sleep(1)
        head("up")
        time.sleep(2)
        arm("up")
        time.sleep(3)
        arm("down")
        audio_trigger("box")
        time.sleep(1)
        audio_trigger("ghost")
        time.sleep(7)
        arm("up")
        audio_trigger("sc")
        time.sleep(2)
        arm("down")
        time.sleep(5)
        ghost_cabinet("close")
        torso("left")
        head("down")
        pass
    elif which == "a_little_head_nod":
        torso("right")
        time.sleep(.5)
        head("up")
        time.sleep(1)
        audio_trigger("sc")
        time.sleep(4)
        head("down")
        time.sleep(1)
        head("Up")
        time.sleep(1)
        torso("left")
        time.sleep(2)
        head("down")
    elif which == "ghost_cabinet":
        ghost_cabinet("open")
        time.sleep(1)
        audio_trigger("box")
        time.sleep(4)
        audio_trigger("box")
        time.sleep(1)
        audio_trigger("ghost")
        time.sleep(15)
        ghost_cabinet("close")
        pass
    elif which == "scare_crow":
        torso("right")
        time.sleep(.5)
        head("up")
        time.sleep(2)
        audio_trigger("sc")
        time.sleep(3)
        arm("up")
        head("down")
        time.sleep(1)
        arm("down")
        head("up")
        audio_trigger("sc")
        time.sleep(4)
        torso("left")
        time.sleep(1)
        arm("down")
        torso("right")
        time.sleep(1)
        arm("up")
        time.sleep(1)
        audio_trigger("sc")
        time.sleep(4)
        torso("left")
        time.sleep(2)
        arm("down")
        head("down")
        pass

def main():
    # main loop condition
    haunted_porch = True
    loop_waits = [30, 45, 60, 15]
    possible_motions = ["the_works", "a_little_head_nod", "ghost_cabinet", "scare_crow"]

    # reset everything
    porch_motion("reset")
    time.sleep(60)

    # main loop
    while haunted_porch:
        # run a motion
        porch_motion(random.choice(possible_motions))
        porch_motion("scare_crom")
        time.sleep(1)
        porch_motion("the_works")
        time.sleep(30)
        haunted_porch = False


if __name__ == "__main__":
    main()
