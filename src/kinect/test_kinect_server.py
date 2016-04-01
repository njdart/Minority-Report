#!/usr/bin/python

from kinect_server import KinectServer
from threading import Thread
import time

if __name__ == "__main__":
    srv = KinectServer()
    thread = Thread(target=srv.BeginLoop, args=[])
    thread.start()
    while 1:
        pass
    srv.EndLoop()
