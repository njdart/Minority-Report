import io

import cv2
import numpy
import datetime
from flask_socketio import emit
from src.model.Canvas import Canvas
from src.model.User import User
from src.model.Postit import Postit
from src.model.Image import Image
from flask import send_from_directory, send_file
from werkzeug.exceptions import NotFound
from src.server import (app, socketio)
import os


@socketio.on('getUsers')
def getUsers():
    emit('getUsers', [user.as_object() for user in User.get_all()])


@socketio.on('addUser')
def addUser(details):
    emit('addUser', User(username=details["username"]).create().as_object())


@socketio.on('getUser')
def getUser(details):
    emit('getUser', User.get(id=details["id"]).as_object())


@socketio.on('updateUser')
def updateUser(details):
    username = details["username"]
    id = details["id"]

    user = User.get(id=id)

    if not user:
        emit('updateUser', False)
        return

    if username != user.get_username():
        user.set_username(username)
        user.update()

    emit('updateUser', user.as_object())


@socketio.on('deleteUser')
def deleteUser(details):
    id = details["id"] if "id" in details else None

    emit('deleteUser', User.get(id=id).delete().as_object())


@socketio.on('addImage')
def addImage(details):
    userId = details["user"]
    # EG "2016-04-09T13:04:50.148Z"
    timestamp = datetime.datetime.strptime(details["timestamp"], '%Y-%m-%dT%H:%M:%S.%fZ')
    file = details["file"]

    arr = numpy.fromstring(file, numpy.uint8)
    npArr = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    emit('addImage', Image(user=userId,
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


@socketio.on('getCanvases')
def getCanvases():
    emit('getCanvases', [canvas.as_object() for canvas in Canvas.get_all()])


@socketio.on('getPostits')
def getPostits():
    emit('getPostits', [postit.as_object() for postit in Postit.get_all()])


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

    image = canvas.get_canvas_unkeystoned()

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
