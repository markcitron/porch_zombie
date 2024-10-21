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

## What is running where
| Device      | Description     |    Player     |
|-------------|-----------------|---------------|
| pz_0        | SPST Relay, with Motion Sensor| Motion sensor and simple triggers near Ghost Cabinet: Raven, Cherub, Electricution Box, Gourdo, Ghost |
| pz_1        | SPST Relay, with Motion Sensor | Motion sensor and simple triggers near Tilting Alien: Jumping Spider, Plague Doctor, Jack-o-lantern |
| pz_2        | Heavy Relay (3) | Ghost Cabinet Left door, Ghost Cabinet Right door, Baby head in a box|
| pz_3        | Light Relay (8) | Tilting Alien, Skull Picture|


---
## Required packages
- RPi.GPIO
- gpiozero (using LED and Motion Sensor

---
## Motion
I have triggered motion in the past bye using the Pi Camera and/or USB camera and runniong the motion service and then trailing the application log file and looking for **motion_detected** events.

For this year, just using IR sensor attached to the two SPST relay bots, PZ_0 and Pz_1

## Sequencing
| Activity | Action | Wait before next call |
|----------|--------|-----------------------|
| Skull peak a boo | extend | 2|
| Skull peak a boo | contract | 5 |
| Wake the raven | trigger | 2 |
| Open Baby Box | contract | 1 |
| Plague Dr. | Relay.on() | 1 |
| Plague Dr. | Relay.off() | 9 |
| Close Baby Box | extend | 4 |
| Hello Pumpkin | on | 1 |
| Hello Puppkin | off | 1 |
| Tilt Alien | extend | 1 |
| Sad Little Skull | contract | 3 |
| Sad Little Skull | extend | 3 |
| Tilt Alien Back | contract | 1 |
| Ghost Cabinet (open) | extend 2 | .5 |
| Ghost Cabinet (open) | extend 3 | 3 |
| Wake Ghost | trigger | 15 |
| Ghost Cabinet (close) | contract 2 | .5 |
| Ghost Cabinet (close) | contract 3 | 3 |
| Wake Ghost | trigger | 1 |
| Wake Raven | trigger | 2 |
| Tile Alien (hello) | extend | 1 |
| Sad Little Skull | contract | 3 |
| Sad Little Skull | extend | 3 |
| Tile Alien (bye) | contract | 1 |
| ... Wait to reset ... | ... do nothing ... | 30 |


---
## Yearly efforts - archives
- [Servo based zombie - 2020](./archive/2020) - Simple zombie frame powered by 22kg capactiy servo motor to move the parts around.  Was awesome until it caught fire :-)
- [Actuators and Steppers - 2021](./archive/2021) - Uses Flask based API for main controller, **Haunted Porch** to control the other raspberry pis
- [External controller - 2022](./archive/2022)
- 2023 - a more wholistic approach to building this repo.  No breakdowns by year, just code designed to be easily leveragable.
--- 
