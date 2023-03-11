#!/usr/bin/python3

from flask import Flask, render_template
import time

# linear actuator controller pid
pz1 = "10.10.0.3"

app = Flask(__name__)

@app.route('/')
def the_haunted_porch():
    return render_template('index.html')

@app.route('/empty_page.html')
def show_empty_page():
    return render_template("empty_page.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0')
