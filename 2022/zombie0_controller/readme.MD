# zombie0 - the main controller
This pi runs the camera trigger(s) as well as calls the other zombies.  All of the Pis are running Flask and communidation is via the web api calls.

## Required modules
- flask - for the web api interfaces
- psutil - to check the running processes to show what is running, etc.
- cv2 - our OpenCV friend.  Previous motion detection was using the **motion** service.  It is noisy and doesn't allow us to do additional image processing ourside of the motion detection
- argparse - argument parser

## Scripts
- main.py - starts up the main flask application
- motion_trigger.py - script that runs **OpenCV** and calls the other zombies to bring the haunted porch to life
- zombie.py - takes argument [start|stop] and either starts or stops both the **main.py** and **motion_trigger.py** scripts.  They are launched via **screen** as background tasks.
