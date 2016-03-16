"""
The Controller is built on top of a HTTP server, in order to simplify interop
between managed code (Kinect-based data) and Python code (everything else,
presumably).

The server shall expect the Kinect-handling client to make a connection on a
port, specified below as SERVER_PORT. The following requests are handled:

    GESTURE
    BODIES

Each of these will also send a HTTP body in the form of plain-text JSON data.

-----------------------------
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

-----------------------------
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

SERVER_PORT = 13337
SERVER_HOST = "localhost"

class Controller(HTTPServer):
    """
    This class acts as the controller for the Minority Report application. It
    accepts connections from the Kinect-handling managed-code application (it
    also starts up this application itself).
    """
    def __init__(self, server_address, server_class):
        print(server_class)
        HTTPServer.__init__(server_address, server_class)

    def _spawnKinectClient(self):
        """
        Spawns the managed executable which handles Kinect data. (TODO)
        """
        pass

class ControllerRequestHandler(BaseHTTPRequestHandler):
    def do_GESTURE(self):
        pass

    def do_BODIES(self):
        pass

    def do_GET(self):
        print("somebody GET'd")


if __name__ == "__main__":
    ctrl = HTTPServer((SERVER_HOST, SERVER_PORT), ControllerRequestHandler)
    ctrl.serve_forever()
