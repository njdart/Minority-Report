import io
import cv2
from flask import send_file
from flask.ext.socketio import emit
from werkzeug.exceptions import NotFound
from src.model.Postit import Postit
from src.server import (app, socketio)


@socketio.on('get_postits')
def getPostits():
    emit('get_postits', [postit.as_object() for postit in Postit.get_all()])


@socketio.on('create_postit')
def create_postit(canvas, colour, corners):
    emit('create_postit', Postit(canvas=canvas,
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


@socketio.on('update_postit')
def update_canvas(id, canvas, colour, corners):
    postit = Postit.get(id=id)

    postit.canvas = canvas
    postit.colour = colour
    postit.topLeftX = corners["topLeft"]["x"] if "topLeft" in corners else None
    postit.topLeftY = corners["topLeft"]["y"] if "topLeft" in corners else None
    postit.topRightX = corners["topRight"]["x"] if "topRight" in corners else None
    postit.topRightY = corners["topRight"]["y"] if "topRight" in corners else None
    postit.bottomLeftX = corners["bottomLeft"]["x"] if "bottomLeft" in corners else None
    postit.bottomLeftY = corners["bottomLeft"]["y"] if "bottomLeft" in corners else None
    postit.bottomRightX = corners["bottomRight"]["x"] if "bottomRight" in corners else None
    postit.bottomRightY = corners["bottomRight"]["y"] if "bottomRight" in corners else None

    emit('update_canvas', postit.update().as_object())


@socketio.on('delete_postit')
def delete_postit(id):
    emit('delete_postit', Postit.get(id=id).delete())


@app.route('/api/postit/<postitId>')
def postit_serve(postitId):

    postit = Postit.get(id=postitId)

    if postit is None:
        raise NotFound()

    image = postit.get_postit_image()

    if image is None:
        raise NotFound()

    i = cv2.imencode('.jpg', image)[1].tostring()
    return send_file(io.BytesIO(i), mimetype='image/jpg')


@socketio.on("purge_postits")
def purge_postits():
    for p in Postit.get_all():
        p.delete()

print('Registered Postit API methods')
