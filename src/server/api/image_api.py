import datetime
import cv2
import numpy
import os
import uuid
from flask import send_from_directory
from flask.ext.socketio import emit
from src.model.Image import Image
from src.server import (app, socketio)


@socketio.on('create_image')
def create_image(file, createdAt, instanceConfigurationId):

    arr = numpy.fromstring(file, numpy.uint8)
    npArr = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    emit('create_image', Image(npArray=npArr,
                               timestamp=createdAt,
                               id=uuid.uuid4(),
                               instanceConfigurationId=instanceConfigurationId).create().as_object())


@socketio.on('get_images')
def get_images():
    emit('get_images', [image.as_object() for image in Image.get_all()])


@socketio.on('delete_image')
def deleteImage(id):
    emit('delete_image', Image.get(id=id).delete().as_object())


@socketio.on('update_image')
def updateImage(id, timestamp, instanceConfigurationId):
    image = Image.get(id=id)

    image.timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    image.instanceConfigurationId = instanceConfigurationId

    emit('update_image', image.update().as_object())


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


@socketio.on('get_image')
def get_image(instanceConfigurationId, uri):
    print('Getting image from URI ', uri)
    image = Image.from_uri(uri=uri, instanceConfigurationId=instanceConfigurationId)

    if image is None:
        emit('addImageFromUri', None)
        return

    emit('create_image', image.create().as_object())


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

    path = os.path.join(root_dir, '..', 'static', 'images')
    file = '{}.jpg'.format(imageId)

    try:
        return send_from_directory(path, file, mimetype='image/jpg')
    except:
        return send_from_directory(path, "testPostit1.jpg", mimetype="image/jpg")

print('Registered Image API methods')
