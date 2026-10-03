#!/usr/bin/python3

import time
import RPi.GPIO as GPIO
from relays import LinAct, gpio_cleanup

PIR_PIN = 5
ZOMBIE_CLOSET_PIN = 26
MIN_TRIGGER_TIME = 0.30
COOLDOWN = 2.0
FIRE_TIME = 1.0

def open_zombie_closet(relay):
	print("Activating Zombie Closet")
	relay.contract()
	try:
		time.sleep(FIRE_TIME)
	finally:
		relay.extend()


def main():
	GPIO.setup(PIR_PIN, GPIO.IN)
	relay1 = LinAct("Zombie Closet", ZOMBIE_CLOSET_PIN)
	relay1.extend()
	last_trigger = 0.0

	print("Zombie Closet motion trigger running...")

	try:
		while True:
			now = time.time()

			if now - last_trigger < COOLDOWN:
				time.sleep(0.05)
				continue

			if GPIO.input(PIR_PIN):
				start = time.monotonic()
				while GPIO.input(PIR_PIN):
					time.sleep(0.01)
				duration = time.monotonic() - start

				if duration >= MIN_TRIGGER_TIME:
					print(f"Valid motion! Duration: {duration:.2f}s")
					open_zombie_closet(relay1)
					last_trigger = time.time()
				else:
					print(f"Ignored small motion ({duration:.2f}s)")

			time.sleep(0.05)
	except KeyboardInterrupt:
		print("Exiting...")
	finally:
		relay1.extend()
		gpio_cleanup()


if __name__ == "__main__":
	main()
