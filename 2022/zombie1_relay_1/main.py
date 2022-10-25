#!/usr/bin/python3

from flask import Flask, render_template
from relays import *
import time
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

app = Flask(__name__)

# relay_status
relay_status = {
        "relay_one": "0",
        "relay_two": "0",
        "relay_three": "0",
        "relay_four": "0",
        "relay_five": "0",
        "relay_six": "0",
        "relay_seven": "0",
        "relay_eight": "0",
        "automation_one": "off"
        }

def get_latest_relay_status():
    relay_status["relay_one"] = lib8relind.get(0, 1)
    relay_status["relay_two"] = lib8relind.get(0, 2)
    relay_status["relay_three"] = lib8relind.get(0, 3)
    relay_status["relay_four"] = lib8relind.get(0, 4)
    relay_status["relay_five"] = lib8relind.get(0, 5)
    relay_status["relay_six"] = lib8relind.get(0, 6)
    relay_status["relay_seven"] = lib8relind.get(0, 7)
    relay_status["relay_eight"] = lib8relind.get(0, 8)
    return True

def set_all_relay_statuses(value):
    relay_status["relay_one"] = value
    relay_status["relay_two"] = value
    relay_status["relay_three"] = value
    relay_status["relay_four"] = value
    relay_status["relay_five"] = value
    relay_status["relay_six"] = value
    relay_status["relay_seven"] = value
    relay_status["relay_eight"] = value
    return True

def ok_for_direct_relay_control():
    if relay_status["automation_one"] == "on":
        return False
    else:
        return True

@app.route('/')
def relay_mainpage():
    get_latest_relay_status()
    return render_template('index.html', current_status=relay_status)

@app.route('/someone_is_here/')
def someone_is_here():
    get_latest_relay_status()
    if ok_for_direct_relay_control():
        print("Someone is here!!!")
        # motions
        time.sleep(1)
        relay3.contract() # reset electrocution
        relay3.extend() # trigger electrocution
        time.sleep(2)
        relay8.extend() # torso swist
        time.sleep(1)
        relay7.extend() # raise head
        time.sleep(1)
        relay1.extend() # extend right arm
        relay2.extend() # extend right arm
        time.sleep(1)
        relay4.contract() # reset scarecrow voice
        relay4.extend() # scarecrow says hi
        time.sleep(.1)
        relay5.contract() # reset ghost trigger
        relay5.extend() # trigger ghost
        time.sleep(2)
        relay7.contract()
        time.sleep(1)
        relay7.extend()
        relay1.contract()
        relay2.contract()
        time.sleep(2)
        relay1.extend()
        relay2.extend()
        relay7.contract()
        time.sleep(1)
        relay7.extend()

        # second motion
        time.sleep(4)
        relay8.contract() # torso twist
        relay1.contract() # rt arm down
        relay2.contract() # rt arm down
        time.sleep(1)
        relay8.extend() # torso twise
        relay1.extend() # rt arm up
        relay2.extend() # rt arm up
        relay4.contract() # sc voice trigger reset
        relay4.extend() # sc voice trigger #2


        # set relay statues
        relay_status['relay_one'] = "1"
        relay_status['relay_two'] = "1"
        relay_status['relay_seven'] = "1"
        relay_status['relay_eight'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/they_are_gone/')
def they_are_gone():
    get_latest_relay_status()
    if ok_for_direct_relay_control():
        print("They're gone, bye bye.")
        relay3.extend()
        relay3.contract()
        relay1.contract()
        relay2.contract()
        relay7.contract()
        relay8.contract()
        relay_status['relay_one'] = "0"
        relay_status['relay_two'] = "0"
        relay_status['relay_seven'] = "0"
        relay_status['relay_eight'] = "0"
        time.sleep(1)
        relay3.extend()
        relay3.contract()
    return render_template("index.html", current_status=relay_status)


@app.route('/extend_one/')
def extend_one():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay1.extend() 
        relay_status['relay_one'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_one/')
def contract_one():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay1.contract() 
        relay_status['relay_one'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_two/')
def extend_two():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay2.extend() 
        relay_status['relay_two'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_two/')
def contract_two():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay2.contract() 
        relay_status['relay_two'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_three/')
def extend_three():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay3.extend() 
        relay_status['relay_three'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_three/')
def contract_three():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay3.contract() 
        relay_status['relay_three'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_four/')
def extend_four():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay4.extend() 
        relay_status['relay_four'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_four/')
def contract_four():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay4.contract() 
        relay_status['relay_four'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_five/')
def extend_five():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay5.extend() 
        relay_status['relay_five'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_five/')
def contract_five():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay5.contract() 
        relay_status['relay_five'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_six/')
def extend_six():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay6.extend() 
        relay_status['relay_six'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_six/')
def contract_six():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay6.contract() 
        relay_status['relay_six'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_seven/')
def extend_seven():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay7.extend() 
        relay_status['relay_seven'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_seven/')
def contract_seven():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay7.contract() 
        relay_status['relay_seven'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_eight/')
def extend_eight():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay8.extend() 
        relay_status['relay_eight'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_eight/')
def contract_eight():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        relay8.contract() 
        relay_status['relay_eight'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_right_arm/')
def extend_right_arm():
    get_latest_relay_status()
    if ok_for_direct_relay_control():
        relay1.extend()
        relay2.extend()
        relay_status['relay_one'] = "1"
        relay_status['relay_two'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_right_arm/')
def contract_right_arm():
    get_latest_relay_status()
    if ok_for_direct_relay_control():
        relay1.contract()
        relay2.contract()
        relay_status['relay_one'] = "0"
        relay_status['relay_two'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/turn_all_on/')
def turn_all_relays_on():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        lib8relind.set_all(0,255) 
        set_all_relay_statuses("1")
    return render_template("index.html", current_status=relay_status)

@app.route('/turn_all_off/')
def turn_all_relays_off():
    get_latest_relay_status()
    if ok_for_direct_relay_control(): 
        lib8relind.set_all(0,0) 
        set_all_relay_statuses("0")
    return render_template("index.html", current_status=relay_status)

@app.route('/automation_one_on/')
def turn_automation_one_on():
    get_latest_relay_status()
    # don't run unless it is in the off state
    if relay_status["automation_one"] == "off":
        relay_status["automation_one"] = "on" 
    return render_template("index.html", current_status=relay_status)

@app.route('/automation_one_off/')
def turn_automation_one_off():
    get_latest_relay_status()
    # don't stop unless it is in the on state
    if relay_status["automation_one"] == "on":
        relay_status["automation_one"] = "off" 
    return render_template("index.html", current_status=relay_status)

@app.errorhandler(Exception)
def basic_error(e):
    return "an error occurred: " + str(e)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
