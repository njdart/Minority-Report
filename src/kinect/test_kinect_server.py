from kinect_server import KinectServer
from threading import Thread
import time

if __name__ == "__main__":
    srv = KinectServer()
    thread = Thread(target=srv.BeginLoop, args=(srv,))
    thread.start()
    time.sleep(2)
    srv.EndLoop()
