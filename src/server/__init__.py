from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

from src.server import ui
from src.server import kinect
from src.server import api
from src.model.Model import Model

def run_server():

    model = Model()
    socketio.run(app, host="0.0.0.0", port=8088, debug=True)

if __name__ == '__main__':
    run_server()
