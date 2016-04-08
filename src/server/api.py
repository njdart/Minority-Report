from server import (app, socketio)
from flask_socketio import send, emit
import numpy as np
from PIL import Image
import io
import base64

import cv2

def npArray2Base64(npArray):
    img = Image.fromarray(npArray)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
    # $('div').css('background-image', 'url(data:image/gif;base64,' + a.image + ')');

@socketio.on('getPostits')
def getPostits(request):
    print("Get Postits" + str(request))
    emit('getPostits', [
        {
            "canvas": "de305d54-75b4-431b-adb2-eb6b9e546014",
            "id": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
            "image": npArray2Base64(cv2.imread('/home/nic/Downloads/postit.jpg')),
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

