from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})

def update(canvas):
    """
    This method can be called by the model to broadcast a canvas update to all listening clients
    :param canvas: model/Canvas/Canvas class
    :return: None
    """
    pass


if __name__ == '__main__':
    socketio.run(app)