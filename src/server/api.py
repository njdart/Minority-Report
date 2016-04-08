from server import (app, socketio)

@socketio.on('getPostits')
def getPostits(request):
    emit('getPostits', [
        {
            "canvas": "de305d54-75b4-431b-adb2-eb6b9e546014",
            "id": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
            "image": "base64-encoded image: see http://stackoverflow.com/questions/26331787/socket-io-node-js-simple-example-to-send-image-files-from-server-to-client",
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
        }
    })

