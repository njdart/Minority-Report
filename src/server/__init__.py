from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def update(canvas):
    """
    This method can be called by the model to broadcast a canvas update to all listening clients
    :param canvas: model/Canvas/Canvas class
    :return: None
    """
    pass

from server import misc
from server import kinect
from server import ui

def run_server():
    socketio.run(app, host="0.0.0.0", port=8088, debug=True)

if __name__ == '__main__':
    run_server()
