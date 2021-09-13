#!/usr/bin/python3

from flask import Flask
from relays import *

app = Flask(__name__)

@app.route('/')
def hello_world():
    r_one_test()
    return 'Hello World'

@app.route('/relay_one_test/')
def test_relay_one():
    #return r_one_test()
    return "hello again"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
