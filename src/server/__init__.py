from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

from server import ui
from server import kinect
from server import api

def run_server():
    socketio.run(app, host="0.0.0.0", port=8088, debug=True)

if __name__ == '__main__':
    run_server()
