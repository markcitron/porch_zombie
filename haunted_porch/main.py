#!/usr/bin/python3

from flask import Flask, render_template
import psutil
import requests, time

app = Flask(__name__)

""" Flask web endpoints """
@app.route('/')
def hello():
    return render_template('index.html')
    # return render_template('index.html', param1=value1, param2=value2)

@app.route('/launcher_status/')
def launcher_status():
    launcher_script = "None"
    launcher_pid = 0
    launcher_running = "No"
    for p in psutil.process_iter():
        if "launcher" in p.name():
            launcher_script = p.name();
            launcher_pid = p.pid
            launcher_running = "Yes"
    return render_template('launcher_status.html', script_name=launcher_script, script_id=launcher_pid, script_status=launcher_running)

@app.errorhandler(Exception)
def basic_error(e):
    return("an error occurred: " + str(e))

def main():
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()
