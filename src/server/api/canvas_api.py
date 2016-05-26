import cv2
import io
from flask import send_file
from flask.ext.socketio import emit
from werkzeug.exceptions import NotFound
from src.model.Canvas import Canvas
from src.server import (app, socketio)


@socketio.on('get_canvases')
def get_canvases():
    emit('get_canvases', [canvas.as_object() for canvas in Canvas.get_all()])


@socketio.on('create_canvas')
def create_canvas(session, derivedAt, derivedFrom, width, height):
    emit('create_canvas', Canvas(session=session,
                                 derivedAt=derivedAt,
                                 derivedFrom=derivedFrom,
                                 width=width,
                                 height=height)
         .create().as_object())


@socketio.on('delete_canvas')
def delete_canvas(id):
    emit('delete_canvas', Canvas.get(id=id).delete())


@socketio.on('update_canvas')
def update_canvas(id, session, derivedFrom, derivedAt, width, height):
    canvas = Canvas.get(id=id)

    canvas.session = session
    canvas.derivedAt = derivedAt
    canvas.derivedFrom = derivedFrom
    canvas.width = width
    canvas.height = height

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


@socketio.on("purge_canvases")
def purge_canvases():
    Canvas.delete_all()



print('Registered Canvas API methods')

