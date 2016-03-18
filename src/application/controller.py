"""
This is the top-level module of the application, containing the Controller
class.
"""

import kinect_server
import model
import ui_server
import camera_client

import threading
import time

class MinorityReportController:
    """
    This is the top level class for the Minority Report application. It
    initialises:
    - REST server for communication with Kinect client application
    - The Model (extracts graphs from images)
    - Web server to serve user client applications (viewer, admin panel, etc.)
    - Web client to receive images from smartphone
    """
    def __init__(self):
        """Initialises the controller."""
        self.kinectServer = kinect_server.KinectServer()
        self.uiServer     = ui_server.UIServer()
        self.model        = None # TODO
        self.cameraClient = None # TODO

        self.kinectServerThread = None

    def Go(self):
        """
        Pretty self-explanatory method. Returns upon user-requested shutdown.
        """
        # Kinect server startup (separate thread)
        self.kinectServerThread = threading.Thread(
            target = self.kinectServer.BeginLoop)
        self.kinectServerThread.start()

        # UI server startup
        self.uiServer.Start()

        # Camera client startup

        # TODO : this is actually meant to be an infinite loop
        # while 1:
        #     pass
        # time.sleep(5)

    def Cleanup(self):
        """Cleans up objects, threads, etc."""
        # TODO
        self.kinectServer.EndLoop()
        self.kinectServerThread.join()
