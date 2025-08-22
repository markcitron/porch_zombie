#!/usr/bin/python3

class ModeManager:
    def __init__(self):
        self.mode = "patrol"
        self.cooldown = 0

    def update_mode(self, movement_detected):
        if self.mode == "patrol" and movement_detected:
            self.mode = "tracking"
            self.cooldown = 30  # frames or seconds
        elif self.mode == "tracking":
            if self.cooldown > 0:
                self.cooldown -= 1
            else:
                self.mode = "patrol"

    def get_mode(self):
        return self.mode
