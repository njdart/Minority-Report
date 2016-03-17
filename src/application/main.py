from controller import MinorityReportController
import sys

def parse_args():
    for arg in sys.argv[1:]:
        if (arg == "-h") or (arg == "--help"):
            print("## MINORITY REPORT ##")
            print("This program does not take any parameters. Simply run it. To terminate it")
            print("manually, press Ctrl+C.")
            print()
            print("Have fun!")
            exit()
        else:
            print("Unrecognised parameter '" + arg + "'.")
            exit()

if __name__ == "__main__":
    parse_args()
    ctrl = MinorityReportController()
    try:
        ctrl.begin_loop()
    except KeyboardInterrupt:
        print("User requested manual shutdown. Stopping...")
        ctrl.shutdown()
else:
    raise RuntimeError("This module should only serve as an entry point!")
