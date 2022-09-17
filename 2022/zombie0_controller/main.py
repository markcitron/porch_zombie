#!/usr/bin/python3

from flask import Flask, render_template
import psutil

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

def main():
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()
