# PZ_0_SPST_Relay
This is a Single Pull Single Throw (SPST) relay hat sitting on top of a RaspberryPi 4.  As it is a 4, there is also a cooling fan between the relay hat and the main board.  This SPST board only takes up 8 pins and shares a ground.  The pins can be controlled using **GPIOZero** to turn them on or off by referring to them as LEDs:
```
from gpiozero import LED
relay_x = LED(pin)
relay_x.on() or relay_x.off() or relay_x_trigger()
```
**On()** and **Off()** are self-explanatory. The **trigger()** call pulses on for a second and then off.  This will work well for the types of devices that I am triggering.
Because this is simple pin mapping hat, you can still use the other pins for things like a motion sensor.  For the motion sensor:

```
from gpiozero import MotionSensor
ms = MotionSensor(pin)
ms.when_motion = function_to_call
```

## Triggers
- IR Sensor - simple sensor to fire when someone is walking along the path up to the porch, just past the garage door
- OpenCV - going to get a little fancier and see if we can have OpenCV detect different people coming up and not flag for certain folks. For this, I'll start with stuff that I have done in the past but heavily used Copilot to help generate code and a trainable model.
