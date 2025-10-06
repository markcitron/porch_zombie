#!/usr/bin/python

import time
import lib8relind
from relays import *

# set up linear actuator relays
relay1 = LinAct("", 1)
relay2 = LinAct("", 2)
relay3 = LinAct("", 3)
relay4 = LinAct("", 4)
relay5 = LinAct("", 5)
relay6 = LinAct("", 6)
relay7 = LinAct("", 7)
relay8 = LinAct("", 8)

def extend_all_relays():
    realy1.extend()
    realy2.extend()
    realy3.extend()
    realy4.extend()
    realy5.extend()
    realy6.extend()
    realy7.extend()
    realy8.extend()
    return True

def contract_all_relays():
    realy1.contract()
    realy2.contract()
    realy3.contract()
    realy4.contract()
    realy5.contract()
    realy6.contract()
    realy7.contract()
    realy8.contract()
    return True

def main():

if __name__ == "__main__":
    main()
