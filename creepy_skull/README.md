# Creepy Skull Setup Instructions

## Auto-Start mqtt_skull_motion.py on Raspberry Pi Boot

1. **Make the script executable:**
   ```bash
   chmod +x /home/pi/my_repos/porch_zombie/creepy_skull/mqtt_skull_motion.py
   ```

2. **Create a systemd service file:**
   ```bash
   sudo nano /etc/systemd/system/mqtt_skull_motion.service
   ```
   Add the following:
   ```
   [Unit]
   Description=Creepy Skull MQTT Motion Script
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /home/pi/my_repos/porch_zombie/creepy_skull/mqtt_skull_motion.py
   WorkingDirectory=/home/pi/my_repos/porch_zombie/creepy_skull
   StandardOutput=inherit
   StandardError=inherit
   Restart=always
   User=pi

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service:**
   ```bash
   sudo systemctl enable mqtt_skull_motion
   sudo systemctl start mqtt_skull_motion
   ```

4. **Check the service status:**
   ```bash
   sudo systemctl status mqtt_skull_motion
   ```


---

## Changing Service Restart Behavior

If you do not want the service to always restart automatically, edit the systemd service file and change:

```
Restart=always
```
to:
```
Restart=no
```
or use other options like `on-failure`, `on-abort`, or `on-success` for more control.

After editing, reload systemd:
```bash
sudo systemctl daemon-reload
```
Then restart or stop the service as needed.

---

The script will now run automatically on boot!
