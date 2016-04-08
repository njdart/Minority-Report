from server import (app, socketio)

@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})
