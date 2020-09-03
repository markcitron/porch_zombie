# porch_zombie
Every year I try to build something cool, funny challenging to celebrate Halloween, just the coolest holiday.  Last year, I built some automated opening and closing creepy crates and a really crappy motion controlled bot on a wire that was supposed to go back and forth across my porch.  I say crappy as stretching string and trying to do fine positioning with micro servos and low grade steppers were my downfall.

This year is the year of the Porch Zombie, a Raspberry Pi controlled automaton.  Inputs, etc., include:
- Adafruit Servo kit controlled servos (not the mini plastic ones, the better ones that can move 22 Kgs)
- Camera with OpenCv2  for motion detection, etc.  Could use simple sensor, but I have been working on something that uses histogram deltas to determine motion and think that it might be more fun here.
- Wooden automaton skeleton (by me) and a custom set of painted freeky masks from my artisic 15 year old son.  This should rock and, even if it doesn't work, will be fun :-)

## Required packages
- adafruit - `pip3 install adafruit-circuitpython-servokit`, 
- OpenCv2 (version - whatever you'd like)
