# Porch Zombie: Haunted Porch Automation
Welcome to the Haunted Porch project! This year, we've moved from a Flask-based multi-Raspberry Pi setup to a robust MQTT-driven architecture for controlling all our Halloween bots and effects.

## Project Overview
- Main Bots:

  - **Coffin Skeleton:** Controls a linear actuator to raise/lower a skeleton. MQTT-triggered.
  - **Creepy Skull:** Animates a skull with servos and motion. MQTT-triggered.
  - **Crypt Keeper:** Controls multiple relays for lights, effects, and actuators. MQTT-triggered.
  - **Mad Scientist:** The central trigger and controller bot. Detects motion, runs the main trigger sequence, and provides a FastAPI UI for manual control and status.
  - **Haunted Porch Controller:** Used for manual control and testing. Not part of the main automated trigger flow.

## 2025 Architecture
- **MQTT:** All bots now communicate via MQTT messages. Each bot listens for its trigger keyword and executes its effect.

- **Triggers:**

  - Primary: Simple PIR motion detectors.
  - Secondary: OpenCV with a low-light webcam for advanced tracking (in development).
  - Future: LIDAR and additional sensors for more precise activation.
- **Actuators:**

  - **Current:** Servos and linear actuators.
  - **Next Year:** Stepper motors for improved control and articulation.

## Main Bots
### Coffin Skeleton
- Script: [mqtt_cs_and_ec.py](./coffin_skeleton/mqtt_cs_and_ex.py)
- Listens for `coffin_skeleton` and `electro_closet` MQTT triggers.
- Controls linear actuators via relays.
- Prevents overlapping actions with threading locks.
### Creepy Skull
- Script: [mqtt_skull_motion.py](./creepy_skull/mqtt_skull_motion.py)
- Animates skull using servos.
- Listens for `creepy_skull` MQTT trigger.
- Can be auto-started via systemd.
### Crypt Keeper
- Script: [mqtt_crypt_keeper.py](./crypt_keeper/mqtt_crypt_keeper.py)
- Controls up to 8 relays for effects.
- Listens for `crypt_keeper_#` MQTT trigger, where # is the number of the relay.  Currently:
  - relay_1 - **Scarecrow voice**
  - relay_2 - **Talking Jack-o-lantern**
- Uses GPIO and threading locks for safe relay control.
### Mad Scientist (Main Trigger & Control)
- Script: [mqtt_main_trigger.py](./mad_scientist/mqtt_main_trigger.py)
- Detects motion (PIR sensor on GPIO23).
- Publishes a configurable sequence of MQTT triggers to all bots.
- Plays sound effects during trigger sequence.
- FastAPI UI (ui.py) for manual control, log viewing, and testing.
### Scarecrow
- Script: [mqtt_scarecrow.py](scarecrow/mqtt_scarecrow.py)
- Controls relay(s) for scarecrow movement or effects.
- Listens for `scarecrow` MQTT trigger.
- Uses GPIO and threading locks for safe relay control.

## Manual Control & Testing
- **Haunted Porch Controller (main.py)**:
  - FastAPI web UI for manual testing and control.
  - Not part of the main automated flow, but useful for setup and diagnostics.
## Triggers & Sensors
 - **PIR Motion Detectors:** Main trigger for the sequence.
  - **OpenCV + Low-Light Camera:** Secondary trigger and porch tracking (in development).
  - **LIDAR:** Planned for future upgrades.
## Requirements
- **Python 3.7+** on all Raspberry Pis.  
- **MQTT Broker** (e.g., Mosquitto) running on your network.
- **Python Modules:**
  - paho-mqtt
  - gpiozero
  - fastapi, uvicorn (for UI)
  - pygame (for sound playback)
  - simpleaudio, numpy (for sound testing)
- **System Updates:**
  - sudo apt update && sudo apt upgrade
  - sudo apt install python3-venv python3-pip python3-gpiozero
- **Install Python dependencies (example for Mad Scientist bot):
```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install paho-mqtt fastapi uvicorn simpleaudio numpy pygame
```

## Running the Bots
- Each bot runs its own script and listens for MQTT triggers.
- The Mad Scientist bot runs the main trigger sequence and UI.
- Use systemd services for auto-start on boot (see each bot's README for details).

## Future Plans
- Add stepper motors for advanced movement and articulation.
- Integrate LIDAR and more advanced sensors.
- Expand OpenCV tracking for more interactive effects.

## Archive
- Link: [Archive](./archive/)
- Old work dating back to 2020