import RPi.GPIO as GPIO
import time

PIR_PIN = 5   # BCM numbering for physical pin 29

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

print("PIR Test Running... (Ctrl+C to exit)")
time.sleep(2)  # allow PIR to settle

try:
    while True:
        if GPIO.input(PIR_PIN):
            print("Motion detected!")
        else:
            print("No motion")
        time.sleep(0.2)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Exiting...")
