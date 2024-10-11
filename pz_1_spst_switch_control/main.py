#!/usr/bin/python3

from flask import Flask, render_template
from gpiozero import LED
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

# set up spst switches (treating them as LEDs)
# board basically just calls pics and shares a ground
sw_1 = LED(5)
sw_2 = LED(6)
sw_3 = LED(13)
sw_4 = LED(16)
sw_5 = LED(19)
sw_6 = LED(20)
sw_7 = LED(21)
sw_8 = LED(26)

# initialize flask app
app = Flask(__name__)

@app.route('/')
def main_landing():
    return render_template('index.html')

@app.errorhandler(Exception)
def basic_error(e):
    return "an error occurred: " + str(e)

if __name__ == "__main__":
    app.run(host='0.0.0.0')

def main():
    print("started up and waiting ...")
    while True:
        motion.when_motion = someone_is_here
    return True

if __name__ == "__main__":
    main()
