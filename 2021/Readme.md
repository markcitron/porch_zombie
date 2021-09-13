# POrch Zombie 2021

## Relay Controlled Actuators
Uses api calls, through Flask, to trigger relay controlled linear actuators.  These calls can be hit directly through the web interface or from the **Zombie Alpha** controller app running on the primary **Haunted Porch** controller.
Files:
- relay_controller.py - main api listener, Flask based
- relays.py - Classes to control things
- templates directory - for the html templates Flash uses
