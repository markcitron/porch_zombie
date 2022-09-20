#!/usr/bin/python3

from flask import Flask, render_template
from relays import *
import time

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
        "relay_one": "contracted",
        "relay_two": "contracted",
        "relay_three": "contracted"
        }

@app.route('/')
def relay_mainpage():
    return render_template('index.html')

@app.route('/extend_one/')
def extend_one():
    relay1.extend()
    relay_status['relay_one'] = "extended"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_one/')
def contract_one():
    relay1.contract()
    relay_status['relay_one'] = "contracted"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_two/')
def extend_two():
    relay2.extend()
    relay_status['relay_two'] = "extended"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_two/')
def contract_two():
    relay2.contract()
    relay_status['relay_two'] = "contracted"
    return render_template("index.html", current_status=relay_status)

@app.route('/extend_three/')
def extend_three():
    relay3.extend()
    relay_status['relay_three'] = "extended"
    return render_template("index.html", current_status=relay_status)

@app.route('/contract_three/')
def contract_three():
    relay3.contract()
    relay_status['relay_three'] = "contracted"
    return render_template("index.html", current_status=relay_status)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
