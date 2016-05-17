from flask.ext.socketio import emit
from src.server import socketio
from src.model.InstanceConfiguration import InstanceConfiguration


@socketio.on('create_instance_configuration')
def create_instance_configuration(sessionId,
                                  userId,
                                  cameraHost,
                                  cameraPort,
                                  kinectHost,
                                  kinectPort):
    """
    Create an instance configuration
    :param sessionId: string the id of a session
    :param userId: string the id of a user
    :param cameraHost: string the host of a camera
    :param cameraPort: string the port of a camera
    :param kinectHost: string the host of a kinect
    :param kinectPort: string the port of a kinect
    :return: an instance configuration object eg:
    {
        "sessionId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "userId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "kinectHost": "localhost",
        "kinectPort": 8080,
        "cameraHost": "localhost",
        "cameraPort": "8080",
        "topLeftX": 0,
        "topLeftY": 0,
        "topRightX": 100,
        "topRightY": 0,
        "bottomRightX": 100,
        "bottomRightY": 100,
        "bottomLeftX": 0,
        "bottomLeftY": 100,
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    }
    """
    emit('create_instance_configuration', InstanceConfiguration(sessionId=sessionId,
                                                                userId=userId,
                                                                cameraHost=cameraHost,
                                                                cameraPort=cameraPort,
                                                                kinectHost=kinectHost,
                                                                kinectPort=kinectPort).create().as_object())

print('Registered Instance Configuration API methods')
