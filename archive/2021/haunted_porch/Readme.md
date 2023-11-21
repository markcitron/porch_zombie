# Haunted Porch - main controller
This pi serves as the main controller for the **Zombies** on our **Haunted Porch**.  This pi is running the service **Motion** to keep track of people that we want to use as triggers. This utilizes **Flask** as web based control.  The main scripts uses `wget` in system calls to the APIs on the **Zombies** to control motion.
## Motion service
Motion is set to start automaticall and is a service. Useful commands:
- `sudo service status motion` - show the status of the motion service
- `sudo service motion stop|start` - to stop or start the motion service
## Active Files
- [hp_controller.py](./hp_controller.py)
- [motion_trigger.py](./motion_trigger.py)
## Require installs
- Flask - `pip3 install Flask`