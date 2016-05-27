from flask.ext.socketio import emit
from src.server import socketio
from time import sleep
from src.model.InstanceConfiguration import InstanceConfiguration


@socketio.on('create_instance_configuration')
def create_instance_configuration(details):
    """
    Create an instance configuration
    :param details: object details about the instance configuration
    :param details["sessionId"] string id of a session
    :param details["userId"] string id of a user
    :param details["cameraHost"] string host of the camera
    :param details["cameraPort"] integer port of the camera
    :param details["kinectHost"] string host of the kinect
    :param details["kinectPort"] integer port of the kinect
    :param details["topLeft"] object details about the topLeft calibration coordinate (Optional)
    :param details["topLeft"]["x"] integer the X coordinate of the topLeft point
    :param details["topLeft"]["y"] integer the Y coordinate of the topLeft point
    :param details["topRight"] object details about the topRight calibration coordinate (Optional)
    :param details["topRight"]["x"] integer the X coordinate of the topRight point
    :param details["topRight"]["y"] integer the Y coordinate of the topRight point
    :param details["bottomLeft"] object details about the bottomLeft calibration coordinate (Optional)
    :param details["bottomLeft"]["x"] integer the X coordinate of the bottomLeft point
    :param details["bottomLeft"]["y"] integer the Y coordinate of the bottomLeft point
    :param details["bottomRight"] object details about the bottomRight calibration coordinate (Optional)
    :param details["bottomRight"]["x"] integer the X coordinate of the bottomRight point
    :param details["bottomRight"]["y"] integer the Y coordinate of the bottomRight point
    :return: an instance configuration object eg:
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "sessionId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "userId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "kinect": {
            "host": "localhost",
            "port": 8080,
        },
        "camera": {
            "host": "localhost",
            "port": "8080",
        },
        "topLeft": {
            "x": 0,
            "y": 100
        },
        "topRight": {
            "x": 0,
            "y": 100
        },
        "bottomRight": {
            "x": 0,
            "y": 100
        },
        "bottomLeft": {
            "x": 0,
            "y": 100
        }
    }
    """
    config = InstanceConfiguration(sessionId=details["sessionId"],
                                   userId=details["userId"],
                                   cameraHost=details["camera"]["host"],
                                   cameraPort=details["camera"]["port"],
                                   kinectHost=details["kinect"]["host"],
                                   kinectPort=details["kinect"]["port"],
                                   topLeftX=details["topLeft"]["x"] if "topLeft" in details else None,
                                   topLeftY=details["topLeft"]["y"] if "topLeft" in details else None,
                                   topRightX=details["topRight"]["x"] if "topRight" in details else None,
                                   topRightY=details["topRight"]["y"] if "topRight" in details else None,
                                   bottomRightX=details["bottomRight"]["x"] if "bottomRight" in details else None,
                                   bottomRightY=details["bottomRight"]["y"] if "bottomRight" in details else None,
                                   bottomLeftX=details["bottomLeft"]["x"] if "bottomLeft" in details else None,
                                   bottomLeftY=details["bottomLeft"]["y"] if "bottomLeft" in details else None)
    emit('create_instance_configuration', config.create().as_object())


@socketio.on('get_instance_configurations')
def get_instance_configurations():
    emit('get_instance_configurations', [cfg.as_object() for cfg in InstanceConfiguration.get_all()])


@socketio.on('delete_instance_configuration')
def delete_instance_configuration(configurationId):
    emit('delete_instance_configuration', InstanceConfiguration.get(configurationId).delete())


@socketio.on('update_instanceConfig')
def update_instanceConfig(id, details):
    print(id)
    print(details)
    config = InstanceConfiguration.get(id=id)

    config.sessionId = details["sessionId"]
    config.userId = details["userId"]
    config.cameraHost = details["camera"]["host"]
    config.cameraPort = details["camera"]["port"]
    config.kinectHost = details["kinect"]["host"]
    config.kinectPort = details["kinect"]["port"]
    config.topLeftX = details["topLeft"]["x"] if "topLeft" in details else None
    config.topLeftY = details["topLeft"]["y"] if "topLeft" in details else None
    config.topRightX = details["topRight"]["x"] if "topRight" in details else None
    config.topRightY = details["topRight"]["y"] if "topRight" in details else None
    config.bottomRightX = details["bottomRight"]["x"] if "bottomRight" in details else None
    config.bottomRightY = details["bottomRight"]["y"] if "bottomRight" in details else None
    config.bottomLeftX = details["bottomLeft"]["x"] if "bottomLeft" in details else None
    config.bottomLeftY = details["bottomLeft"]["y"] if "bottomLeft" in details else None

    emit('update_instanceConfig', config.update().as_object())


@socketio.on('calibrate_instance_configuration')
def calibrate_instance_configuration(instanceConfigId):
    """
    Calibrate an instance configuration by trying to connect to the camera and auto-extracting projector bounds
    """
    print('Calibrating instance configuration {}'.format(instanceConfigId))
    emit('blank_canvas_white', broadcast=True)
    sleep(0.5)
    ic = InstanceConfiguration.get(id=instanceConfigId).calibrate().update()
    print('Calibrated')
    emit('calibrate_instance_configuration', ic.as_object())
    emit('blank_canvas_black', broadcast=True)


@socketio.on('purge_instance_configurations')
def purge_instance_configurations():
    InstanceConfiguration.delete_all()

@socketio.on('get_latest_image_id_by_instance_configuration')
def get_latest_image_id_by_instance_configuration(instanceConfigId):
    ic = InstanceConfiguration.get(instanceConfigId)
    emit('get_latest_image_id_by_instance_configuration', ic.get_latest_image_id())


print('Registered Instance Configuration API methods')
