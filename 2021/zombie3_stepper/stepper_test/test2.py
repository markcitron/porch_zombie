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
	Motor1.SetMicroStep('softward','fullstep')
	Motor1.TurnStep(Dir='backward', steps=20000, stepdelay = 0.00001)
        """
	time.sleep(0.5)
	Motor1.TurnStep(Dir='backward', steps=20000, stepdelay = 0.00001)
	time.sleep(0.5)
	Motor1.TurnStep(Dir='forward', steps=10000, stepdelay = 0.00001)
        """

	Motor1.Stop()
    
except:
    # GPIO.cleanup()
    print "\nMotor stop"
    Motor1.Stop()
    exit()
