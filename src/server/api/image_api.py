import datetime
import cv2
import numpy
import os
from flask import send_from_directory
from flask.ext.socketio import emit
from src.model.Image import Image
from src.server import (app, socketio)


@socketio.on('addImage')
def addImage(details):
    timestamp = datetime.datetime.strptime(details["timestamp"], '%Y-%m-%dT%H:%M:%S.%fZ')
    file = details["file"]

    arr = numpy.fromstring(file, numpy.uint8)
    npArr = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    emit('addImage', Image(sessionId=1,
                           npArray=npArr,
                           timestamp=timestamp).create().as_object())


@socketio.on('getImages')
def getImages():
    emit('getImages', [image.as_object() for image in Image.get_all()])


@socketio.on('deleteImage')
def deleteImage(details):
    emit('deleteImage', Image.get(details["id"]).delete().as_object())


@socketio.on('updateImage')
def updateImage(details):
    image = Image.get(details["id"])

    timestamp = datetime.datetime.strptime(details["timestamp"], '%Y-%m-%dT%H:%M:%S.%fZ')

    image.set_timestamp(timestamp)
    emit('updateImage', image.update().as_object())


@socketio.on('autoExtractCanvas')
def autoExtractCanvas(image_id):
    image = Image.get(image_id)

    if image is None:
        emit('autoExtractCanvas', None)
        return

    canvas = image.find_canvas()
    if canvas is None:
        emit('autoExtractCanvas', None)
        return

    emit('autoExtractCanvas', canvas.as_object())


@socketio.on('addImageFromUri')
def addImageFromUri(uri):
    image = Image.from_uri(uri=uri)

    if image is None:
        emit('addImageFromUri', None)
        return

    emit('addImageFromUri', image.create().as_object())


@socketio.on('cameraFocus')
def cameraFocus(uri):
    emit('cameraFocus', Image.focus_camera(uri))


@socketio.on('getCameraProperties')
def getCameraProperties(uri):
    emit('getCameraProperties', Image.get_camera_properties(uri))


@socketio.on('setCameraProperties')
def setCameraProperties(uri, properties):
    emit('setCameraProperties', Image.set_camera_properties(uri, properties=properties))


@app.route('/api/image/<imageId>')
def image_serve(imageId):

    root_dir = os.path.dirname(os.path.realpath(__file__))

    path = os.path.join(root_dir, 'static', 'images')
    file = '{}.jpg'.format(imageId)

    try:
        return send_from_directory(path, file, mimetype='image/jpg')
    except:
        return send_from_directory(path, "testPostit1.jpg", mimetype="image/jpg")

print('Registered Image API methods')
