import cv2
import io
from flask import send_file
from flask.ext.socketio import emit
from werkzeug.exceptions import NotFound
from src.model.Canvas import Canvas
from src.server import (app, socketio)
import datetime


@socketio.on('get_canvases')
def get_canvases():
    emit('get_canvases', [canvas.as_object() for canvas in Canvas.get_all()])


@socketio.on('create_canvas')
def create_canvas(image, derivedAt, derivedFrom, corners):
    emit('create_canvas', Canvas(image=image,
                                 derivedAt=derivedAt,
                                 derivedFrom=derivedFrom,
                                 canvasTopLeftX=corners["topLeft"]["x"] if "topLeft" in corners else None,
                                 canvasTopLeftY=corners["topLeft"]["y"] if "topLeft" in corners else None,
                                 canvasTopRightX=corners["topRight"]["x"] if "topRight" in corners else None,
                                 canvasTopRightY=corners["topRight"]["y"] if "topRight" in corners else None,
                                 canvasBottomLeftX=corners["bottomLeft"]["x"] if "bottomLeft" in corners else None,
                                 canvasBottomLeftY=corners["bottomLeft"]["y"] if "bottomLeft" in corners else None,
                                 canvasBottomRightX=corners["bottomRight"]["x"] if "bottomRight" in corners else None,
                                 canvasBottomRightY=corners["bottomRight"]["y"] if "bottomRight" in corners else None)
         .create().as_object())


@socketio.on('delete_canvas')
def delete_canvas(id):
    emit('delete_canvas', Canvas.get(id=id).delete())


@socketio.on('update_canvas')
def update_canvas(id, image, derivedFrom, derivedAt, corners):
    canvas = Canvas.get(id=id)

    canvas.image = image
    canvas.derivedAt = derivedAt
    canvas.derivedFrom = derivedFrom
    canvas.canvasTopLeftX = corners["topLeft"]["x"] if "topLeft" in corners else None
    canvas.canvasTopLeftY = corners["topLeft"]["y"] if "topLeft" in corners else None
    canvas.canvasTopRightX = corners["topRight"]["x"] if "topRight" in corners else None
    canvas.canvasTopRightY = corners["topRight"]["y"] if "topRight" in corners else None
    canvas.canvasBottomLeftX = corners["bottomLeft"]["x"] if "bottomLeft" in corners else None
    canvas.canvasBottomLeftY = corners["bottomLeft"]["y"] if "bottomLeft" in corners else None
    canvas.canvasBottomRightX = corners["bottomRight"]["x"] if "bottomRight" in corners else None
    canvas.canvasBottomRightY = corners["bottomRight"]["y"] if "bottomRight" in corners else None

    emit('update_canvas', canvas.update().as_object())


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
