#!/usr/bin/python3

from flask import Flask, render_template
import psutil
import requests, time

app = Flask(__name__)

""" Flask web endpoints """
@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/motion_status/')
def motion_status():
    motion_script = "None"
    motion_pid = 0
    for p in psutil.process_iter():
        if "motion_trigger" in p.name():
            motion_script = p.name()
            motion_pid = p.pid
    return render_template('motion_status.html', script_name=motion_script, script_id=motion_pid)

@app.route('/someone_is_here/')
def someone_is_here():
    x = requests.get('http://10.10.0.14:5000/someone_is_here/')
    y = requests.get('http://10.10.0.83:5000/extend_all')
    return render_template('index.html')

@app.route('/they_are_gone/')
def they_are_gone():
    x = requests.get('http://10.10.0.14:5000/they_are_gone/')
    y = requests.get('http://10.10.0.83:5000/contract_all')
    return render_template('index.html')


@app.errorhandler(Exception)
def basic_error(e):
    return "An error occurred: " + str(e)

def main():
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()
