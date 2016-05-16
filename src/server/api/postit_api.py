import io
import cv2
from flask import send_file
from flask.ext.socketio import emit
from werkzeug.exceptions import NotFound
from src.model.Postit import Postit
from src.server import (app, socketio)


@socketio.on('getPostits')
def getPostits():
    emit('getPostits', [postit.as_object() for postit in Postit.get_all()])


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

print('Registered Postit API methods')
