#!/usr/bin/python

from kinect_server import KinectServer
import time

if __name__ == "__main__":
    srv = KinectServer()
    srv.Start()
    while 1:
        try:
            pass
        except KeyboardInterrupt:
            srv.Stop()
