#!/usr/bin/python3

from flask import Flask, render_template
import psutil
import requests 
from time import sleep

# set global flask app
app = Flask(__name__)

# set componant locations
relay_1 = LED(5)
relay_2 = LED(6)
relay_3 = LED(13)
relay_4 = LED(16)
relay_5 = LED(19)
relay_6 = LED(20)
relay_7 = LED(21)
relay_8 = LED(26)

""" Flask web endpoints """
@app.route('/')
def hello():
    return render_template('index.html')
    # return render_template('index.html', param1=value1, param2=value2)

# Relay 1
@app.route('relay_1_on')
def relay_1_on():
    try: 
        relay_1.on()
    except Exception as e:
        print("Error occured trying to turn relay_1 on: {0}".format(e))
    return True
@app.route('relay_1_off')
def relay_1_off():
    try:
        relay_1.off()
    except Exception as e:
        print("Error occured trying to turn relay_1 off: {0}".format(e))
    return True
@app.route('relay_1_trigger')
def relay_1_trigger():
    try:
        relay_1_on()
        sleep(1)
        relay_1_off()
        sleep(1)
    except Exception as e:
        print("Error occered when trying to trigger ralay_1: {0}".format(e))
    return True

# Relay 2
@app.route('relay_2_on')
def relay_2_on():
    try: 
        relay_2.on()
    except Exception as e:
        print("Error occured trying to turn relay_2 on: {0}".format(e))
    return True
@app.route('relay_2_off')
def relay_2_off():
    try:
        relay_1.off()
    except Exception as e:
        print("Error occured trying to turn relay_2 off: {0}".format(e))
    return True
@app.route('relay_2_trigger')
def relay_1_trigger():
    try:
        relay_2_on()
        sleep(1)
        relay_2_off()
        sleep(1)
    except Exception as e:
        print("Error occered when trying to trigger ralay_2: {0}".format(e))
    return True

# Relay 3
@app.route('relay_3_on')
def relay_3_on():
    try: 
        relay_3.on()
    except Exception as e:
        print("Error occured trying to turn relay_3 on: {0}".format(e))
    return True
@app.route('relay_3_off')
def relay_3_off():
    try:
        relay_3.off()
    except Exception as e:
        print("Error occured trying to turn relay_3 off: {0}".format(e))
    return True
@app.route('relay_3_trigger')
def relay_3_trigger():
    try:
        relay_3_on()
        sleep(1)
        relay_3_off()
        sleep(1)
    except Exception as e:
        print("Error occered when trying to trigger ralay_3: {0}".format(e))
    return True

# Relay 4
@app.route('relay_4_on')
def relay_4_on():
    try: 
        relay_4.on()
    except Exception as e:
        print("Error occured trying to turn relay_4 on: {0}".format(e))
    return True
@app.route('relay_4_off')
def relay_4_off():
    try:
        relay_4.off()
    except Exception as e:
        print("Error occured trying to turn relay_4 off: {0}".format(e))
    return True
@app.route('relay_4_trigger')
def relay_4_trigger():
    try:
        relay_4_on()
        sleep(1)
        relay_4_off()
        sleep(1)
    except Exception as e:
        print("Error occered when trying to trigger ralay_4: {0}".format(e))
    return True

# Relay 5
@app.route('relay_5_on')
def relay_5_on():
    try: 
        relay_5.on()
    except Exception as e:
        print("Error occured trying to turn relay_5 on: {0}".format(e))
    return True
@app.route('relay_5_off')
def relay_5_off():
    try:
        relay_5.off()
    except Exception as e:
        print("Error occured trying to turn relay_5 off: {0}".format(e))
    return True
@app.route('relay_5_trigger')
def relay_1_trigger():
    try:
        relay_5_on()
        sleep(1)
        relay_5_off()
        sleep(1)
    except Exception as e:
        print("Error occered when trying to trigger ralay_5: {0}".format(e))
    return True

# Relay 6
@app.route('relay_6_on')
def relay_6_on():
    try: 
        relay_6.on()
    except Exception as e:
        print("Error occured trying to turn relay_6 on: {0}".format(e))
    return True
@app.route('relay_6_off')
def relay_6_off():
    try:
        relay_6.off()
    except Exception as e:
        print("Error occured trying to turn relay_6 off: {0}".format(e))
    return True
@app.route('relay_6_trigger')
def relay_6_trigger():
    try:
        relay_6_on()
        sleep(1)
        relay_6_off()
        sleep(1)
    except Exception as e:
        print("Error occered when trying to trigger ralay_6: {0}".format(e))
    return True

# Relay 7
@app.route('relay_7_on')
def relay_7_on():
    try: 
        relay_7.on()
    except Exception as e:
        print("Error occured trying to turn relay_7 on: {0}".format(e))
    return True
@app.route('relay_7_off')
def relay_7_off():
    try:
        relay_7.off()
    except Exception as e:
        print("Error occured trying to turn relay_7 off: {0}".format(e))
    return True
@app.route('relay_7_trigger')
def relay_7_trigger():
    try:
        relay_7_on()
        sleep(1)
        relay_7_off()
        sleep(1)
    except Exception as e:
        print("Error occered when trying to trigger ralay_7: {0}".format(e))
    return True

# Relay 8
@app.route('relay_8_on')
def relay_8_on():
    try: 
        relay_8.on()
    except Exception as e:
        print("Error occured trying to turn relay_8 on: {0}".format(e))
    return True
@app.route('relay_8_off')
def relay_8_off():
    try:
        relay_8.off()
    except Exception as e:
        print("Error occured trying to turn relay_8 off: {0}".format(e))
    return True
@app.route('relay_8_trigger')
def relay_8_trigger():
    try:
        relay_8_on()
        sleep(1)
        relay_8_off()
        sleep(1)
    except Exception as e:
        print("Error occered when trying to trigger ralay_8: {0}".format(e))
    return True

@app.route('/launcher_status/')
def launcher_status():
    launcher_script = "None"
    launcher_pid = 0
    launcher_running = "No"
    for p in psutil.process_iter():
        if "watchful_zombie" in p.name():
            launcher_script = p.name();
            launcher_pid = p.pid
            launcher_running = "Yes"
    return render_template('launcher_status.html', script_name=launcher_script, script_id=launcher_pid, script_status=launcher_running)

@app.errorhandler(Exception)
def basic_error(e):
    return("An error occurred: " + str(e))

def main():
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()
