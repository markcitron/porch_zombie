#!/usr/bin/python3

from flask import Flask, render_template
from relays import *
import time
import lib8relind

# set up linear actuator relays
relay1 = LinAct("Scarecrow_head_tilt", 1)
relay2 = LinAct("Scarecrow_torso_twist", 2)
relay3 = LinAct("Scarecrow_trigger_voice", 3)
# relay4 = LinAct("", 4)
# relay5 = LinAct("", 5)
# relay6 = LinAct("", 6)
# relay7 = LinAct("", 7)
# relay8 = LinAct("", 8)

app = Flask(__name__)

# relay_status
relay_status = {
        "relay_one": "0",
        "relay_two": "0",
        "relay_three": "0"
        }

def get_latest_relay_status():
    relay_status["relay_one"] = lib8relind.get(0, 1)
    relay_status["relay_two"] = lib8relind.get(0, 2)
    relay_status["relay_three"] = lib8relind.get(0, 3)
    return True

@app.route('/')
def relay_mainpage():
    get_latest_relay_status()
    return render_template('index.html', current_status=relay_status)

@app.route('/extend_one/')
def extend_one():
    get_latest_relay_status()
    relay1.extend()
    relay_status['relay_one'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_one/')
def contract_one():
    get_latest_relay_status()
    relay1.contract()
    relay_status['relay_one'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_two/')
def extend_two():
    get_latest_relay_status()
    relay2.extend()
    relay_status['relay_two'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_two/')
def contract_two():
    get_latest_relay_status()
    relay2.contract()
    relay_status['relay_two'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_three/')
def extend_three():
    get_latest_relay_status()
    relay3.extend()
    relay_status['relay_three'] = "1"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_three/')
def contract_three():
    get_latest_relay_status()
    relay3.contract()
    relay_status['relay_three'] = "0"
    return render_template("index.html", current_status=relay_status)

@app.errorhandler(Exception)
def basic_error(e):
    return "an error occurred: " + str(e)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
