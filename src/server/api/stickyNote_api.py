import io
import cv2
from flask import send_file
from flask.ext.socketio import emit
from werkzeug.exceptions import NotFound
from src.model.StickyNote import StickyNote
from src.server import (app, socketio)
import base64


@socketio.on('get_stickyNotes')
def getStickyNotes():
    emit('get_stickyNotes', [stickyNote.as_object() for stickyNote in StickyNote.get_all()])


@socketio.on('create_stickyNote')
def create_stickyNote(canvas, colour, corners):
    emit('create_stickyNote', StickyNote(canvas=canvas,
                                 colour=colour,
                                 topLeftX=corners["topLeft"]["x"] if "topLeft" in corners else None,
                                 topLeftY=corners["topLeft"]["y"] if "topLeft" in corners else None,
                                 topRightX=corners["topRight"]["x"] if "topRight" in corners else None,
                                 topRightY=corners["topRight"]["y"] if "topRight" in corners else None,
                                 bottomRightX=corners["bottomRight"]["x"] if "bottomRight" in corners else None,
                                 bottomRightY=corners["bottomRight"]["y"] if "bottomRight" in corners else None,
                                 bottomLeftX=corners["bottomLeft"]["x"] if "bottomLeft" in corners else None,
                                 bottomLeftY=corners["bottomLeft"]["y"] if "bottomLeft" in corners else None)
         .create().as_object())


@socketio.on('update_stickyNote')
def update_canvas(id, canvas, colour, corners):
    stickyNote = StickyNote.get(id=id)

    stickyNote.canvas = canvas
    stickyNote.colour = colour
    stickyNote.topLeftX = corners["topLeft"]["x"] if "topLeft" in corners else None
    stickyNote.topLeftY = corners["topLeft"]["y"] if "topLeft" in corners else None
    stickyNote.topRightX = corners["topRight"]["x"] if "topRight" in corners else None
    stickyNote.topRightY = corners["topRight"]["y"] if "topRight" in corners else None
    stickyNote.bottomLeftX = corners["bottomLeft"]["x"] if "bottomLeft" in corners else None
    stickyNote.bottomLeftY = corners["bottomLeft"]["y"] if "bottomLeft" in corners else None
    stickyNote.bottomRightX = corners["bottomRight"]["x"] if "bottomRight" in corners else None
    stickyNote.bottomRightY = corners["bottomRight"]["y"] if "bottomRight" in corners else None

    emit('update_canvas', stickyNote.update().as_object())


@socketio.on('delete_stickyNote')
def delete_stickyNote(id):
    emit('delete_stickyNote', StickyNote.get(id=id).delete())


@app.route('/api/stickyNote/<stickyNoteId>')
def stickyNote_serve(stickyNoteId):

    stickyNote = StickyNote.get(id=stickyNoteId)

    if stickyNote is None:
        raise NotFound()

    image = stickyNote.get_image_binarized()

    if image is None:
        raise NotFound()

    i = cv2.imencode('.jpg', image)[1].tostring()
    return send_file(io.BytesIO(i), mimetype='image/jpg')

@app.route('/api/stickyNoteb64/<stickyNoteId>')
def stickyNoteb64_serve(stickyNoteId):

    stickyNote = StickyNote.get(id=stickyNoteId)

    if stickyNote is None:
        raise NotFound()

    image = stickyNote.get_image_binarized()

    if image is None:
        raise NotFound()

    i = cv2.imencode('.jpg', image)[1].tostring()
    b64 = base64.b64encode(i)
    return b64, 200


@socketio.on("purge_stickyNotes")
def purge_stickyNotes():
    StickyNote.delete_all()

print('Registered StickyNote API methods')
