#!/usr/bin/python3

import numpy as np

class MovementDetector:
    def __init__(self, threshold=100, min_points=5, max_points=1000):
        self.prev_scan = None
        self.threshold = threshold
        self.min_points = min_points
        self.max_points = max_points

    def normalize(self, scan):
        scan = np.array(scan)
        if len(scan) > self.max_points:
            return scan[:self.max_points]
        elif len(scan) < self.max_points:
            return np.pad(scan, (0, self.max_points - len(scan)), mode='constant', constant_values=0)
        return scan

    def detect_movement(self, current_scan):
        current = self.normalize(current_scan)

        if self.prev_scan is None:
            self.prev_scan = current
            return False

        delta = np.abs(current - self.prev_scan)
        movement_points = np.sum(delta > self.threshold)

        self.prev_scan = current
        return movement_points >= self.min_points
