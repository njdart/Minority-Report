import base64
import io
import cv2
from PIL import Image
from flask_socketio import emit
from server import (socketio)

def npArray2Base64(npArray):
    img = Image.fromarray(npArray)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
    # $('div').css('background-image', 'url(data:image/gif;base64,' + a.image + ')');

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
                  "image": npArray2Base64(cv2.imread('/home/jashan/Minority-Report/src/server/static/testPostit1.jpg')),
                  "connections": [
                    "36afb67b-c127-4fb8-b795-b917c4099742",
                    "3fb558b4-5c5c-42a1-98db-84267c470a47"
                    ]
                },

                {
                  "postitId": "36afb67b-c127-4fb8-b795-b917c4099742",
                  "realX": 790,
                  "realY": 450,
                  "colour": "red",
                  "image": npArray2Base64(cv2.imread('/home/jashan/Minority-Report/src/server/static/testPostit2.jpg')),
                  "connections": [
                    "23a29456-5ded-4b66-b3f0-178b7afdc0e7"
                  ]
                },

                {
                  "postitId": "3fb558b4-5c5c-42a1-98db-84267c470a47",
                  "realX": 1200,
                  "realY": 970,
                  "colour": "green",
                  "image": npArray2Base64(cv2.imread('/home/jashan/Minority-Report/src/server/static/testPostit1.jpg')),
                  "connections": []
                }
            ]
        }
    )

@socketio.on('getPostits')
def getPostits(request):
    print("Get Postits" + str(request))
    emit('getPostits', [
        {
            "canvas": "de305d54-75b4-431b-adb2-eb6b9e546014",
            "id": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
            "image": npArray2Base64(cv2.imread('/home/jashan/Minority-Report/src/server/statictestPostit1.jpg')),
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
    }
         )