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

@app.errorhandler(Exception)
def basic_error(e):
    return("an error occurred: " + str(e))

def main():
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()