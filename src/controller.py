"""
This is the top-level module of the application, containing the Controller
class.
"""

from src import server


class MinorityReportController(object):
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

    def Go(self):
        """
        Pretty self-explanatory method. Returns upon user-requested shutdown.
        """
        server.run_server()

    def Cleanup(self):
        """
        Cleans up objects, threads, etc.
        """
