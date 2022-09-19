#!/usr/bin/python3

import configparser

config = configparser.ConfigParser()
config.read("./hp.cnf")

print("Name: {0}, ip: {1}".format(config['zombie1_relay_one']['name'],config['zombie1_relay_one']['ip']))
