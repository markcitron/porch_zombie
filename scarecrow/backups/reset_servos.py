#!/usr/bin/python3
from robot_hat import Servo, ADC
from robot_hat.utils import reset_mcu
from time import sleep

reset_mcu()
print("MCU Reset")

sleep(1)
adc0 = ADC(0)
adc1 = ADC(1)
adc2 = ADC(2)
adc3 = ADC(3)
adc4 = ADC(4)

vert_offset = 0
horz_offset = -5

if __name__ == '__main__':
    print("Resetting servos to centers")
    try: 
        Servo(7).angle(0+vert_offset)
        Servo(8).angle(0+horz_offset) 
        sleep(1)
    except:
        print("Unable to reset servos")
