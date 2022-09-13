#!/usr/bin/python3

from flask import Flask, render_template
from relays import *
import time

# set up linear actuator relays
relay1 = LinAct("LinearActuatorOne", 26)
relay2 = LinAct("LinearActuatorTow", 21)
relay3 = LinAct("LinearActuatorThree", 20)

# setting up global relay controls

app = Flask(__name__)

@app.route('/')
def relay_mainpage():
    return render_template('index.html')

@app.route('/extend_one/')
def extend_one():
    relay1.extend()
    return render_template("index.html")

@app.route('/contact_one/')
def contract_one():
    relay1.contact()
    return render_template("index.html")

@app.route('/extend_two/')
def extend_two():
    relay2.extend()
    return render_template("index.html")

@app.route('/contract_two/')
def contract_two():
    relay2.contract()
    return render_template("index.html")

@app.route('/extend_three/')
def extend_three():
    relay3.extend()
    return render_template("index.html")

@app.route('/contract_three/')
def contract_three():
    relay3.contract()
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0')