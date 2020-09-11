#!/usr/bin/python3

import sys

class CLI:
    def __init__(self, name):
        self.name = name
        self.prompt = "{}-> ".format(self.name)
        self.servos = [ 
            {  "name": "rt_upperarm", 
               "id": "s1", 
               "min": 0, 
               "max": 180, 
               "offset": 0 }, 
            {  "name": "rt_elbow",
                "id": "s2",
                "min": 0,
                "max": 180,
                "offset": 0 }, 
            {  "name": "head_pan",
                "id": "s3",
                "min": 0,
                "max": 180,
                "offset": 0 }, 
            {  "name": "head_tile",
                "id": "s4",
                "min": 0,
                "max": 180,
                "offset": 0 }
        ]
        self.commands = [
            { "name": "quit",
              "key_bind": "q",
              "action": self.quit_cli 
              },
            { "name": "List commands",
              "key_bind": "?",
              "action": self.show_commands 
              },
            { "name": "Autonomous Zombine Mode",
              "key_bind": "a",
              "action": self.autonomous_zombie_mode
              },
            { "name": "Interactive Zombine Mode",
              "key_bind": "i",
              "action": self.interactive_zombie_mode
              },
            { "name": "Display Status",
              "key_bind": "s",
              "action": self.display_status
              },
            { "name": "Start Camera",
              "key_bind": "c",
              "action": self.toggle_camera
              },
            { "name": "Set servo values",
              "key_bind": "v",
              "action": self.set_offset
              }
        ]
        self.command_list = []
        for each_command in self.commands:
            self.command_list.append(each_command["key_bind"])
        self.zombie_mode = "active"
        self.camera = "off"

    def set_offset(self):
        servo_list = []
        for each_servo in self.servos:
            servo_list.append(each_servo["id"])
        new_values = {}
        fields = ["name","min","max","offset"]
        while True:
            servo_to_set = input("    |- Servo to set? ") 
            if servo_to_set in servo_list: 
                new_values["id"] = servo_to_set 
                for each_field in fields: 
                    new_values[each_field] = input("    |- ({0}) {1} ? ".format(servo_to_set, each_field)) 
            else: 
                print("    |- servo ids: {0}".format(str(servo_list)))
            if len(new_values) > 1:
                break
        print("new values for {0}: {1}".format(servo_to_set, new_values))

    def toggle_camera(self):
        if self.camera == "off":
            print("  Starting camera ...")
            self.camera = "on"
        else:
            print("  Stopping camera ...")
            self.camera = "off"

    def autonomous_zombie_mode(self):
        self.zombie_mode = "autonomous"

    def interactive_zombie_mode(self):
        self.zombie_mode = "interactive"
    
    def display_status(self):
        print("--------------------------------------------------------------")
        print("- Porch Zombie:") 
        print("  -- Current Zombie Mode: {0}".format(self.zombie_mode))
        print("  -- Camera: {0}".format(self.camera))
        print("  -- Servos:")
        # add in servo information
        for each_servo in self.servos:
            print("    | ({0}) {1} - min: {2}, max: {3}, offset: {4}".format(each_servo["id"], each_servo["name"], each_servo["min"], each_servo["max"], each_servo["offset"]))
        print("")
        print("                                              ? - for options ")
        print("--------------------------------------------------------------")

    def quit_cli(self):
        print("{} closing down ...".format(self.prompt))
        sys.exit(0)

    def show_commands(self):
        for each_command in self.commands:
            print("   ({0}) - {1}".format(each_command['key_bind'], each_command["name"]))

    def validate_command(self, cmd):
        if cmd == "":
            print("  Enter a valid command or ? for list.")
        else:
            cmd = cmd.lower()
            if cmd in self.command_list:
                for each_command in self.commands:
                    if cmd == each_command["key_bind"]:
                        each_command["action"]()
            else:
                print("{0} Invalid command.".format(self.prompt))

    def get_input(self):
        self.validate_command(input(self.prompt))
