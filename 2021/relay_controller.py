#!/usr/bin/python3

from flask import Flask, render_template
from relays import *
import time

# set up linear actuator relays
relay1 = LinArct("LinearActuatorOne", 26)
strobe = LinArct("Strobe", 20)

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/extend_one/')
def extend_one():
    relay1.extend()
    return render_template('index.html')

@app.route('/contract_one/')
def contract_one():
    relay1.contract()
    return render_template('index.html')

@app.route('/trigger_strobe/')
def trigger_strobe():
    strobe.contract()
    time.sleep(1)
    strobe.extend()
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
