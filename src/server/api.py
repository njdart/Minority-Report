import io

import cv2
import numpy
import datetime
from flask_socketio import emit
from src.model.Canvas import Canvas
from src.model.Postit import Postit
from src.model.Image import Image
from flask import send_from_directory, send_file
from werkzeug.exceptions import NotFound
from src.server import (app, socketio)
import os


@socketio.on('addImage')
def addImage(details):
    # EG "2016-04-09T13:04:50.148Z"
    timestamp = datetime.datetime.strptime(details["timestamp"], '%Y-%m-%dT%H:%M:%S.%fZ')
    file = details["file"]

    arr = numpy.fromstring(file, numpy.uint8)
    npArr = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    emit('addImage', Image(npArray=npArr,
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


@socketio.on('getCanvases')
def getCanvases():
    emit('getCanvases', [canvas.as_object() for canvas in Canvas.get_all()])


@socketio.on('getPostits')
def getPostits():
    emit('getPostits', [postit.as_object() for postit in Postit.get_all()])


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

    emit('autoExtractPostits', [ postit.as_object() for postit in postits])


@app.route('/api/image/<imageId>')
def image_serve(imageId):

    root_dir = os.path.dirname(os.path.realpath(__file__))

    path = os.path.join(root_dir, 'static', 'images')
    file = '{}.jpg'.format(imageId)

    try:
        return send_from_directory(path, file, mimetype='image/jpg')
    except:
        return send_from_directory(path, "testPostit1.jpg", mimetype="image/jpg")


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

@socketio.on('getAll')
def getAll(request):
    print("Get all: " + str(request))
    emit("getAll",
        {
            "canvasId": "de305d54-75b4-431b-adb2-eb6b9e546014",
            "timestamp": "2016-03-18T14:02:56.541Z",
            "postits": [
                {
                  "postitId": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
                  "realX": 450,
                  "realY": 450,
                  "colour": "red",
                },

                {
                  "postitId": "36afb67b-c127-4fb8-b795-b917c4099742",
                  "realX": 790,
                  "realY": 450,
                  "colour": "red",
                  "connections": [
                    "23a29456-5ded-4b66-b3f0-178b7afdc0e7"
                  ]
                },

                {
                  "postitId": "3fb558b4-5c5c-42a1-98db-84267c470a47",
                  "realX": 1200,
                  "realY": 970,
                  "colour": "green",
                  "connections": []
                }
            ],
            "connections": {
                "23a29456-5ded-4b66-b3f0-178b7afdc0e7": [
                    "36afb67b-c127-4fb8-b795-b917c4099742",
                    "3fb558b4-5c5c-42a1-98db-84267c470a47"
                ],
                "36afb67b-c127-4fb8-b795-b917c4099742": [
                    "23a29456-5ded-4b66-b3f0-178b7afdc0e7"
                ],
                "3fb558b4-5c5c-42a1-98db-84267c470a47": [
                ]
            }
        }
    )


canvasjson = {
        "id": "de305d54-75b4-431b-adb2-eb6b9e546014",
        "timestamp": "2016-03-18T14:02:56.541Z",
        "postits": [
            {
                "postitId": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
                "realX": 10,
                "realY": 10,
                "colour": "red",
                "connections": [
                    "36afb67b-c127-4fb8-b795-b917c4099742",
                    "3fb558b4-5c5c-42a1-98db-84267c470a47"
                ]
            },
            {
                "postitId": "36afb67b-c127-4fb8-b795-b917c4099742",
                "realX": 10,
                "realY": 10,
                "colour": "red",
                "connections": [
                    "23a29456-5ded-4b66-b3f0-178b7afdc0e7"
                ]
            }
        ]
    }

@socketio.on('getCanvas')
def getCanvas(request):
    print("Get Canvas" + str(request))
    emit('getCanvas', canvasjson)

@socketio.on("updateCanvas")
def updateCanvas(request):
    print("Update Canvas " + str(request))
    socketio.emit("updateCanvas", canvasjson, broadcast=True)


@socketio.on('getSettings')
def getSettings():
    emit('getSettings', {
        "Setting": {
            "value": "Foo",
            "options": [
                "Bar",
                "Baz"
            ]
        }
    })
