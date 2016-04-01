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
            },
        ]
}
"""

import multiprocessing

from flask import Flask
from flask import request
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "hello world"

@app.route("/body")
def body_data():
    return "body data response"

@app.route("/gesture")
def gesture_data():
    return "gesture data response"

@app.route("/shutdown")
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "bye"


class KinectServer:
    def __init__(self):
        self.default_server_name = ""
        self.default_server_port = 13337
        self.stopped = False

    def Start(self):
        self.process = multiprocessing.Process(target = app.run,
                                               args   = ["0.0.0.0", 13337],
                                               kwargs = {"debug": True})
        self.spawn_kinect_client()
        self.process.start()
    
    def Stop(self):
        self.process.terminate()
        self.process.join()
        pass

    def spawn_kinect_client(self):
        """
        Spawns the process which handles Kinect data. (TODO)
        """
        print("Spawning Kinect client...")
