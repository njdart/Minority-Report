from flask import Flask, g
from src.model.databaseHandler import ModelDatabase
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="gevent")

# Prevent the spam of death
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)


def databaseHandler():
    if not hasattr(g, "databaseHandler"):
        g.databaseHandler = ModelDatabase
    return g.databaseHandler()

import src.server.ui
import src.server.kinect
import src.server.api.users_api
import src.server.api.sessions_api
import src.server.api.instanceConfiguration_api
import src.server.api.image_api
import src.server.api.canvas_api
import src.server.api.stickyNote_api

def run_server():
    socketio.run(app, host="0.0.0.0", port=8088, debug=True)

if __name__ == '__main__':
    run_server()
