#!/usr/bin/python3

import sys
from servo_controls import *

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
              "action": go_go_zombie
              },
            { "name": "Display Status",
              "key_bind": "s",
              "action": self.display_status
              },
            { "name": "Start Camera",
              "key_bind": "c",
              "action": self.toggle_camera
              },
            { "name": "Test Arm",
              "key_bind": "t1",
              "action": test_arm
              },
            { "name": "Head - side to side",
              "key_bind": "t2",
              "action": head_side_to_side 
              },
            { "name": "Head - up and down",
              "key_bind": "t3",
              "action": head_up_and_down
              },
            { "name": "Test Head",
              "key_bind": "t4",
              "action": test_head
              },
            { "name": "Look right and point",
              "key_bind": "z1",
              "action": lrap 
              },
            { "name": "no dont think so",
              "key_bind": "z2",
              "action": no_dont_think_so 
              },
            { "name": "Back from LRAP",
              "key_bind": "z3",
              "action": blrap 
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

    def display_status(self):
        print("--------------------------------------------------------------")
        print("- Porch Zombie:") 
        print("  -- Camera: {0}".format(self.camera))
        print("")
        print("                    o     o    O")
        print("                   <|<   <|-  -O~")
        print("                   /\     |\  /} ")
        print("")
        print("                                              ? - for options ")
        print("--------------------------------------------------------------")

    def quit_cli(self):
        print("{} closing down ...".format(self.prompt))
        sys.exit(0)

    def show_commands(self):
        for each_command in self.commands:
            padding = ""
            if len(each_command['key_bind']) == 1:
                    padding = " "
            print("   {0}({1}) - {2}".format(padding, each_command['key_bind'], each_command["name"]))


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
