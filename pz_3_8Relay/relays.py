#!/usr/bin/python3

import time
import lib8relind

class LinAct():
    def __init__ (self, name, relay_id):
        self.name = name
        self.relay_id = relay_id;

    def contract(self):
        lib8relind.set(0, self.relay_id, 1)
        return True

    def extend(self):
        lib8relind.set(0, self.relay_id, 0)
        return True
        
