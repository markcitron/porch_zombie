#!/usr/bin/python3

import time
from threading import Lock

import lib8relind

RELAY_IO_LOCK = Lock()


def set_relay_state(relay_num: int, state: int) -> None:
    with RELAY_IO_LOCK:
        lib8relind.set(0, relay_num, state)


def get_relay_state(relay_num: int) -> int:
    with RELAY_IO_LOCK:
        return lib8relind.get(0, relay_num)


class LinAct():
    def __init__ (self, name, relay_id):
        self.name = name
        self.relay_id = relay_id;

    def extend(self):
        set_relay_state(self.relay_id, 1)
        return True

    def contract(self):
        set_relay_state(self.relay_id, 0)
        return True
        
