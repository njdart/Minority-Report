from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/js/<path:path>')
def js_serve(path):
    return send_from_directory('static/js', path)

@app.route('/styles/<path:path>')
def css_serve(path):
    return send_from_directory('static/styles', path)

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
    socketio.run(app, host="0.0.0.0", port=8088, debug=True)
