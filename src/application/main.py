#!/usr/bin/python
"""
Module serving as the application's entry point.

Warning: Do not import this!
"""

# built-in modules
import sys
import threading

# our modules
from controller import MinorityReportController
from gui import start_gui

help_text = """
## MINORITY REPORT ##
This program does not take any parameters.

Have fun!"""

def parse_args():
    """Interprets command line arguments."""
    for arg in sys.argv[1:]:
        if arg in ["-h", "--help"]:
            print(help_text)
            exit()
        else:
            print("Unrecognised parameter '" + arg + "'.")
            exit()

def start_controller(controller):
    """Starts the controller. Encapsulated for use as a Thread target."""
    controller.begin_loop()

if __name__ == "__main__":
    parse_args()
    ctrl = MinorityReportController()
    ctrl_thread = threading.Thread(target=start_controller,
                                   kwargs={"controller": ctrl})
    ctrl_thread.start()

    # When start_gui returns, we are free to quit.
    start_gui()
    print("Stopping...")
    ctrl.shutdown()
    ctrl_thread.join()
else:
    raise RuntimeError("This module should only serve as an entry point!")
