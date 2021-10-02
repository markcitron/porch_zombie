#!/usr/bin/python3

from flask import Flask, render_template
import time

# setting up global relay controls

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')