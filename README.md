# porch_zombie
Welcome to the **Haunted Porch**


Every year I try to build something cool, funny challenging to celebrate Halloween, just the coolest holiday.  Last year, I built some automated opening and closing creepy crates and a really crappy motion controlled bot on a wire that was supposed to go back and forth across my porch.  I say crappy as stretching string and trying to do fine positioning with micro servos and low grade steppers were my downfall.



## Porch Players
#### RPi controlled ghosts, goblins, etc.
- Skull Picture - tile actuator, rotation (actuator?)
- Jumping Spider (Spirit of Halloween) - trigger only
- Tilting Alien - tilt actuator
- Pumpkin Bench
- Cherub - trigger only
- Baby Head Box - trigger, lid actuator
- Raven - trigger only
- Ghost Cabinet - door actuators, ghost trigger, strobe/light trigger
#### Non-controlled elements
- Haunted Castle
- Mister (water vapor based)
- Popup Pumpkin (Sprit of Halloweed) - Can either use the basic motion detection or wire the trigger like we do with the **Jumping Spider**.

## RPis, how many, who is residing where, etc.
- Haunted Porch (main controller)
  - Camera/OpenCV
  - IR Sensor

---
## Required packages
- adafruit - `pip3 install adafruit-circuitpython-servokit`, 
- OpenCv2 (version - whatever you'd like)
- imutils
- RPi.GPIO
- motion

---
## Motion
I have triggered motion in the past bye using the Pi Camera and/or USB camer and runniong the motion service and then trailing the application log file and looking for **motion_detected** events.


---
## Yearly efforts - archives
- [Servo based zombie - 2020](./archive/2020) - Simple zombie frame powered by 22kg capactiy servo motor to move the parts around.  Was awesome until it caught fire :-)
- [Actuators and Steppers - 2021](./archive/2021) - Uses Flask based API for main controller, **Haunted Porch** to control the other raspberry pis
- [External controller - 2022](./archive/2022)
- 2023 - a more wholistic approach to building this repo.  No breakdowns by year, just code designed to be easily leveragable.
--- 
