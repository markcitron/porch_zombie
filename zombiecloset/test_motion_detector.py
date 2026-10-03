#!/usr/bin/python3
"""Print the zombie closet PIR sensor state once per second."""

import time

import RPi.GPIO as GPIO

PIR_PIN = 5
POLL_INTERVAL = 1.0


def main():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIR_PIN, GPIO.IN)

	print(f"Monitoring PIR sensor on BCM {PIR_PIN}. Press Ctrl+C to stop.")

	try:
		while True:
			motion_active = GPIO.input(PIR_PIN) == GPIO.HIGH
			status = "MOTION (HIGH)" if motion_active else "IDLE (LOW)"
			timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
			print(f"{timestamp} - BCM {PIR_PIN}: {status}", flush=True)
			time.sleep(POLL_INTERVAL)
	except KeyboardInterrupt:
		print("\nExiting...")
	finally:
		GPIO.cleanup(PIR_PIN)


if __name__ == "__main__":
	main()
