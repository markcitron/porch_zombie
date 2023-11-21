#!/usr/bin/python3

import psutil

if __name__ == "__main__":
    for p in psutil.process_iter():
        print("{} {}".format(p.pid, p.name()))
