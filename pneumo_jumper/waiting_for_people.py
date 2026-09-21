#!/usr/bin/python3

import time
import RPi.GPIO as GPIO
from relays import LinAct, gpio_cleanup

PIR_PIN = 5
PNEUMO_JUMPER_PIN = 26
RELAY_2_PIN = 20
MIN_TRIGGER_TIME = 0.30
COOLDOWN = 2.0
FIRE_TIME = 1.0
RELAY_2_START_DELAY = 30.0
RELAY_2_EXTENDED_TIME = 45.0
RELAY_2_RESET_TIME = 30.0


def fire_pneumo_jumper(relay):
	print("Activating Pneumo Jumper")
	relay.contract()
	try:
		time.sleep(FIRE_TIME)
	finally:
		relay.extend()


def run_relay_2_sequence(relay, triggered_at):
	print("Waiting to extend Relay 2")
	elapsed = time.monotonic() - triggered_at
	time.sleep(max(0.0, RELAY_2_START_DELAY - elapsed))
	print("Extending Relay 2")
	relay.extend()
	try:
		time.sleep(RELAY_2_EXTENDED_TIME)
	finally:
		print("Contracting Relay 2")
		relay.contract()
	time.sleep(RELAY_2_RESET_TIME)


def main():
	GPIO.setup(PIR_PIN, GPIO.IN)
	relay1 = LinAct("Pneumo Jumper", PNEUMO_JUMPER_PIN)
	relay2 = LinAct("Relay 2", RELAY_2_PIN)
	relay1.extend()
	relay2.contract()
	last_trigger = 0.0

	print("Pneumo Jumper motion trigger running...")

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
					fire_pneumo_jumper(relay1)
					run_relay_2_sequence(relay2, start)
					last_trigger = time.time()
				else:
					print(f"Ignored small motion ({duration:.2f}s)")

			time.sleep(0.05)
	except KeyboardInterrupt:
		print("Exiting...")
	finally:
		relay1.extend()
		relay2.contract()
		gpio_cleanup()


if __name__ == "__main__":
	main()
