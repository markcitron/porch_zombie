#!/usr/bin/python3
"""Report the raw zombie closet motion sensor signal and transitions."""

import time

import RPi.GPIO as GPIO

PIR_PIN = 6
SAMPLE_INTERVAL = 0.02
REPORT_INTERVAL = 1.0


def state_name(state):
	return "HIGH" if state == GPIO.HIGH else "LOW"


def main():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	print(
		f"Monitoring PIR sensor on BCM {PIR_PIN} (physical pin 31). "
		"Press Ctrl+C to stop."
	)
	print("Move in front of the sensor and watch for HIGH/LOW transitions.")

	try:
		previous_state = GPIO.input(PIR_PIN)
		state_started = time.monotonic()
		next_report = state_started

		while True:
			current_state = GPIO.input(PIR_PIN)
			now = time.monotonic()

			if current_state != previous_state:
				duration = now - state_started
				print(
					f"Signal changed {state_name(previous_state)} -> "
					f"{state_name(current_state)} after {duration:.3f}s",
					flush=True,
				)
				previous_state = current_state
				state_started = now

			if now >= next_report:
				timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
				print(
					f"{timestamp} - BCM {PIR_PIN}: RAW "
					f"{state_name(current_state)}",
					flush=True,
				)
				next_report = now + REPORT_INTERVAL

			time.sleep(SAMPLE_INTERVAL)
	except KeyboardInterrupt:
		print("\nExiting...")
	finally:
		GPIO.cleanup(PIR_PIN)


if __name__ == "__main__":
	main()
