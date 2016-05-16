import cv2
import io
from flask import send_file
from flask.ext.socketio import emit
from werkzeug.exceptions import NotFound
from src.model.Canvas import Canvas
from src.server import (app, socketio)


@socketio.on('getCanvases')
def getCanvases():
    emit('getCanvases', [canvas.as_object() for canvas in Canvas.get_all()])


@socketio.on('autoExtractPostits')
def autoExtractPostits(canvas_id):
    canvas = Canvas.get(canvas_id)

    if canvas is None:
        emit('autoExtractPostits', None)
        return

    postits = canvas.find_postits()

    if postits is None:
        emit('autoExtractPostits', None)
        return

    emit('autoExtractPostits', [postit.as_object() for postit in postits])


@app.route('/api/canvas/<canvasId>')
def canvas_serve(canvasId):

    canvas = Canvas.get(id=canvasId)

    if canvas is None:
        raise NotFound()

    image = canvas.get_canvas_keystoned()

    if image is None:
        raise NotFound()

    i = cv2.imencode('.jpg', image)[1].tostring()
    return send_file(io.BytesIO(i), mimetype='image/jpg')

print('Registered Canvas API methods')
