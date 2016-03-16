"""
The Controller is built on top of a HTTP server, in order to simplify interop
between managed .NET code (Kinect-based data) and Python code (everything else,
presumably).

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


class MinorityReportController(HTTPServer):
    """
    This class acts as the controller for the Minority Report application. It
    accepts connections from the Kinect-handling managed-code application (it
    also starts up this application itself).
    """

    def __init__(self):
        self.server_name = ""
        self.server_port = 13337

        print("Initialising server...")
        HTTPServer.__init__(self,
                            (self.server_name, self.server_port),
                            self.ControllerRequestHandler)

    def spawn_kinect_client(self):
        """
        Spawns the process which handles Kinect data. (TODO)
        """
        print("Spawning Kinect client...")

    def begin_loop(self):
        self.spawn_kinect_client()
        self.serve_forever(poll_interval=0.001)

    def service_actions(self):
        pass

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
