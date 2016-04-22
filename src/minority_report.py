#!/usr/bin/env python3

import sys
from src.controller import MinorityReportController

if __name__ == "__main__":

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

    parse_args()
    ctrl = MinorityReportController()
    print("Starting....")
    ctrl.Go()
    print("Stopping...")
    ctrl.Cleanup()
    exit(0)

else:
    raise RuntimeError("This module should only serve as an entry point!")
