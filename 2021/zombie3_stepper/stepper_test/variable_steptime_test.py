import RPi.GPIO as GPIO
import time
from DRV8825 import DRV8825


try:
	Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))

        how_far = 100000
        step_delay = 0.000001
	Motor1.SetMicroStep('softward','fullstep')

        pos = 0
        current_delay = step_delay
        while pos < 100001: 
                # forward 
                Motor1.TurnStep(Dir='forward', steps=1, stepdelay = current_delay)
                pos = pos + 1
                current_delay = current_delay + 0.000001
                if current_delay > 0.00001:
                    current_delay = step_delay


        time.sleep(1)
        # backward
	Motor1.TurnStep(Dir='backward', steps=how_far, stepdelay = step_delay)
	Motor1.Stop()
    
except:
    # GPIO.cleanup()
    print "\nMotor stop"
    Motor1.Stop()
    exit()
