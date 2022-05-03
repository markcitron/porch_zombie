# Zombie 1 - Actuator controller
This pi has a relay controller had that controlls two actuators and a trigger.  The actuators control the rising behind-the-box zombie.  Utilizes Flask as an api controller that the main, **Haunted Porch**, controller pi triggers via the motion service and a log tailer.
## Active files
- [relay_controller.py](./relay_controller.py) - **Flask** Service receives and processes API calls
- [relays.py](./relays.py) - Relay classes, instantiated in the above controller
- [zombie_motions](./zombie_motions.py) - Contains the **sleep** and **wake** motion functions which are build collections to cause the zombie to wake and sleep.
- [templates dir](./templates) - contains the **Flask** templates called by `relay_controller.py`
## Required installs:
- Flask = `pip3 install flask`