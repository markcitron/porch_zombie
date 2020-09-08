#!/usr/bin/python3

import sys

class CLI:
    def __init__(self, name):
        self.name = name
        self.prompt = "{}-> ".format(self.name)
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
              }
        ]
        self.command_list = []
        for each_command in self.commands:
            self.command_list.append(each_command["key_bind"])
        self.zombie_mode = "active"
        self.camera = "off"

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
        print("  --              Camera: {0}".format(self.camera))
        print("                                              ? - for options ")
        print("--------------------------------------------------------------")

    def quit_cli(self):
        print("{} closing down ...".format(self.prompt))
        sys.exit(0)

    def show_commands(self):
        for each_command in self.commands:
            print("   ({0}) - {1}".format(each_command['key_bind'], each_command["name"]))

    def validate_command(self, cmd):
        if cmd in self.command_list:
            for each_command in self.commands:
                if cmd == each_command["key_bind"]:
                    each_command["action"]()
        else:
            print("{0} Invalid command.".format(self.prompt))

    def get_input(self):
        self.validate_command(input(self.prompt))
