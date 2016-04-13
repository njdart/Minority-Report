from flask import Flask, g
from src.model.databaseHandler import ModelDatabase
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


def databaseHandler():
    if not hasattr(g, "databaseHandler"):
        g.databaseHandler = ModelDatabase
    return g.databaseHandler()

from src.server import ui
from src.server import kinect
from src.server import api


def run_server():

    socketio.run(app, host="0.0.0.0", port=8088, debug=True)

if __name__ == '__main__':
    run_server()
