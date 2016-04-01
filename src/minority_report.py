#!/usr/bin/python
"""
Module serving as the application's entry point.

Warning: Do not import this!
"""

if __name__ == "__main__":

    # built-in modules
    import sys

    # our modules
    from controller import MinorityReportController

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
