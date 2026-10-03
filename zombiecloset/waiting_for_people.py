#!/usr/bin/python3

import time
import RPi.GPIO as GPIO
from relays import LinAct, gpio_cleanup

PIR_PIN = 6
ZOMBIE_CLOSET_PIN = 26
MIN_TRIGGER_TIME = 0.30
COOLDOWN = 2.0
FIRE_TIME = 1.0
POLL_INTERVAL = 0.05

def open_zombie_closet(relay):
	print("Activating Zombie Closet")
	relay.contract()
	try:
		time.sleep(FIRE_TIME)
	finally:
		relay.extend()


def main():
	GPIO.setwarnings(False)
	GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	relay1 = LinAct("Zombie Closet", ZOMBIE_CLOSET_PIN)
	relay1.extend()
	last_trigger = -COOLDOWN
	motion_started = None
	motion_triggered = False

	print("Zombie Closet motion trigger running...")

	try:
		while True:
			now = time.monotonic()
			motion_active = GPIO.input(PIR_PIN) == GPIO.HIGH

			if motion_active:
				if motion_started is None:
					motion_started = now
					motion_triggered = False

				duration = now - motion_started
				cooldown_complete = now - last_trigger >= COOLDOWN
				if (
					not motion_triggered
					and cooldown_complete
					and duration >= MIN_TRIGGER_TIME
				):
					print(f"Valid motion! Duration: {duration:.2f}s")
					open_zombie_closet(relay1)
					last_trigger = time.monotonic()
					motion_triggered = True
			elif motion_started is not None:
				duration = now - motion_started
				if not motion_triggered and duration < MIN_TRIGGER_TIME:
					print(f"Ignored small motion ({duration:.2f}s)")
				motion_started = None
				motion_triggered = False

			time.sleep(POLL_INTERVAL)
	except KeyboardInterrupt:
		print("Exiting...")
	finally:
		relay1.extend()
		gpio_cleanup()


if __name__ == "__main__":
	main()
