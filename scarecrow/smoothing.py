#!/usr/bin/python3

def smooth_angle(prev, current, smoothing=0.3):
    return prev + smoothing * (current - prev)
