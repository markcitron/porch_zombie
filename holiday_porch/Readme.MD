# Holiday Porch 2023
Why should we only have an interesting Halloween Porch and ignore Xmas you ask?

Not anymore ... the Holiday happiness will shine this year (thanks in no small part to my family's urging and me not wanting to wait until next year to play with Pis controlling things)

Building Halloween items is somewhat easy as only the tech needs to be precise.  The build items are supposed to look spooky and broken down, built out of scrap wood, etc.  For the Holiday Porch items, they have to look happy and clean with nice paints and/or decorations.  They have to pass the Rive/Ruby test on holiday cuteness.

## Scope
Going to have three controlled components (all controlled by a single 8 relay Pi) and detector/controller pi that will trigger the porch animation

### Lighted, large Xmas present
- Wrapped with a box that has embedded Xmas lights aroud the permiter
- a simple motor with a rotating bow in the center of the box
- Control(s) required: 
  - - single relay, without switch, to trigger motor

### Tilting Snowman
- Using the tilting alien base from halloween (removed the Alien - he'll be back next year with a paint touch up and varnishing ala Tate the artist).  
- This consists of a simple hinge pivot on a heavy base and controlled via a linear actuator.
- Control(s) required:
  - - single relay, with switch, to tilt snowman

### Opening present
- opening/closing box, wrapped like present with a animated singing stuffy inside (choosing one of the many that we have)
- rewire push started to connect to relay
- Control(s) required:
  - - single relay, with switch, to open/close box
  - - single relay, without switch, to trigger the singing stuffy

### Detector / Controller
- has a single motion detection input and triggers the timing sequence when someone comes onto the porch
- may or maynot include a camera and OpenCV -- if there is time.

## Timing
- Lights on (always)
- Motion detected
- Start Box Rotation
- Box Opens
- Trigger singlging happy snotman
- Snowman tiles out
- (wait for singer to finish)
- Box closes
- Snowman tilts back
- Stop bow rotation

