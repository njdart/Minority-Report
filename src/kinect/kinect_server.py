"""
This module is for communication between the Minority Report application (a
server, essentially) and the .NET application that recieves data from the
Kinect (a client, essentially).

The server shall expect the Kinect-handling client to make a connection on a
port, specified below as SERVER_PORT. The following requests are handled:

    GESTURE
    BODIES

Each of these will also send a HTTP body in the form of plain-text JSON data.

--------------------------------------------------------------------------------
Body data for GESTURE requests

{
    gestures :
        [
            {
                type : <string>,
                x    : <float>,
                y    : <float>
            },
        ]
}

--------------------------------------------------------------------------------
Body data for BODIES requests

{
    bodies :
        [
            {
                topleft_x : <float>,
                topleft_y : <float>,
                width     : <float>,
                height    : <float>
            }
        ]
}
"""

from http.server import (HTTPServer, BaseHTTPRequestHandler)
from http.client import HTTPConnection
import time
from threading import Lock

class KinectServer(HTTPServer):
    """
    This class acts as the controller for the Minority Report application. It
    accepts connections from the Kinect-handling managed-code application (it
    also starts up this application itself).
    """

    def __init__(self):
        self.default_server_name = "localhost"
        self.default_server_port = 13337
        self.stopped = False

        self.handlingLock = Lock()

        print("Initialising server...")
        HTTPServer.__init__(self,
                            (self.default_server_name,
                             self.default_server_port),
                            self.ControllerRequestHandler)

    def BeginLoop(self):
        self.spawn_kinect_client()
        while not self.stopped:
            self.handlingLock.acquire()
            self.handle_request()
            self.handlingLock.release()

            time.sleep(0.001)
        print("Loop has ended")
    
    def EndLoop(self):
        # In order to force the server end its request handling loop,
        # a dummy request must be sent to stop handle_request from
        # blocking. Then, the server is closed in a thread-safe way.
        self.send_dummy_request()

        self.handlingLock.acquire()
        self.server_close()
        self.handlingLock.release()

        self.stopped = True

    def service_actions(self):
        pass

    def send_dummy_request(self):
        conn = HTTPConnection(self.default_server_name,
                              self.default_server_port)
        conn.request("GET", "/")

    def spawn_kinect_client(self):
        """
        Spawns the process which handles Kinect data. (TODO)
        """
        print("Spawning Kinect client...")

    class ControllerRequestHandler(BaseHTTPRequestHandler):
        """
        This class is used to handle requests to the HTTP server by the protocol
        specified at the top of this file.
        """
        def do_GESTURE(self):
            pass

        def do_BODIES(self):
            pass

        def do_GET(self):
            """
            This is the handler for GET requests. Since we don't really care
            about these, we always send a very simple static response.
            """
            self.send_response(200, "hello")
            self.send_header("Content-Length", "11")
            self.end_headers()
            self.wfile.write(b"hello world")