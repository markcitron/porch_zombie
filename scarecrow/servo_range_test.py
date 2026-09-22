#!/usr/bin/python3
from robot_hat import Servo, ADC
from robot_hat.utils import reset_mcu
from time import sleep

reset_mcu()
sleep(1)

adc0 = ADC(0)
adc1 = ADC(1)
adc2 = ADC(2)
adc3 = ADC(3)
adc4 = ADC(4)


if __name__ == '__main__':
    print("Servo library up and running, ready to test ...")
    while True:
        which_servo = input("Servo? ")
        if which_servo == "q":
            print("Thanks for playing :-)")
            break
        servo_moveto = input("Angle? ")
        Servo(int(which_servo)).angle(int(servo_moveto))
