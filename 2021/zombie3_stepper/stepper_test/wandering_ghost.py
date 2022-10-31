import RPi.GPIO as GPIO
import time
from DRV8825 import DRV8825


try:
	Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
	Motor2 = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

	"""
	# 1.8 degree: nema23, nema14
	Motor1.Stop()
	# softward Control :
	# 'fullstep': A cycle = 200 steps
	# 'halfstep': A cycle = 200 * 2 steps
	# '1/4step': A cycle = 200 * 4 steps
	# '1/8step': A cycle = 200 * 8 steps
	# '1/16step': A cycle = 200 * 16 steps
	# '1/32step': A cycle = 200 * 32 steps
	"""
        how_far = 240000
        step_delay = 0.00001

        wander = True
        counter = 0

        while wander: 
            Motor1.SetMicroStep('softward','fullstep') 
            # forward 
            Motor1.TurnStep(Dir='forward', steps=how_far, stepdelay = step_delay) 
            time.sleep(1) 
            # backward 
            Motor1.TurnStep(Dir='backward', steps=how_far, stepdelay = step_delay)

            time.sleep(60) 
            if counter > 30:
                wander = False

            counter += 1

	Motor1.Stop()
    
except:
    # GPIO.cleanup()
    print "\nMotor stop"
    Motor1.Stop()
    exit()
