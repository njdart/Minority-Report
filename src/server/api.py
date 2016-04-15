import cv2
import numpy as np
from PIL import Image as PILImage
import io
import base64
import datetime
from flask_socketio import emit
from server import (socketio, databaseHandler)
from src.model.User import User
from src.model.Image import Image

from flask import send_from_directory
from server import (app, socketio)

def npArray2Base64(npArray):
    img = PILImage.fromarray(npArray)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

@socketio.on('getUsers')
def getUsers():
    emit('getUsers', [user.as_object() for user in databaseHandler().get_users()])


@socketio.on('addUser')
def addUser(details):
    emit('addUser', User(username=details["username"], databaseHandler=databaseHandler()).create().as_object())

@socketio.on('getUser')
def getUser(details):
    username = details["username"] if "username" in details else None
    id = details["id"] if "id" in details else None

    emit('getUser', [{"username": user[1], "id": user[0]} for user in
                     databaseHandler().get_user(username=username, id=id)])

@socketio.on('updateUser')
def updateUser(details):
    username = details["username"] if "username" in details else None
    id = details["id"] if "id" in details else None

    user = databaseHandler().get_user(id=id)

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

    user = databaseHandler().get_user(id=id)

    if user:
        emit('deleteUser', user.delete().as_object())

    else:
        emit('deleteUser', False)

@socketio.on('addImage')
def addImage(details):
    userId = details["user"]
    # EG "2016-04-09T13:04:50.148Z"
    timestamp = datetime.datetime.strptime(details["timestamp"], '%Y-%m-%dT%H:%M:%S.%fZ')
    file = details["file"]

    arr = np.fromstring(file, np.uint8)
    npArr = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    emit('addImage', Image(user=userId,
                           npArray=npArr,
                           timestamp=timestamp,
                           databaseHandler=databaseHandler()).create().as_object())

@socketio.on('getImages')
def getImages():
    emit('getImages', [image.as_object() for image in databaseHandler().get_images()])

@app.route('/images/<postitId>')
def getImage(postitId):
    return send_from_directory("/home/jashan/Minority-Report/src/server/static/", "testPostit1.jpg")

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

@socketio.on('getPostits')
def getPostits(request):
    print("Get Postits" + str(request))
    emit('getPostits', [
        {
            "canvas": "de305d54-75b4-431b-adb2-eb6b9e546014",
            "id": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
            "realX": 10,
            "realY": 10,
            "colour": "red",
            "connections": [
                "36afb67b-c127-4fb8-b795-b917c4099742",
                "3fb558b4-5c5c-42a1-98db-84267c470a47"
            ]
        }
    ])


@socketio.on('getCanvas')
def getCanvas(request):
    print("Get Canvas" + str(request))
    emit('getCanvas', {
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
    })

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
