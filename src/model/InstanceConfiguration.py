import uuid
from src.model.SqliteObject import SqliteObject


class InstanceConfiguration(SqliteObject):
    properties = [
        "id",
        "sessionId",
        "topLeftX",
        "topLeftY",
        "topRightX",
        "topRightY",
        "bottomRightX",
        "bottomRightY",
        "bottomLeftX",
        "bottomLeftY",
        "kinectHost",
        "kinectPort",
        "cameraHost",
        "cameraPort"
    ]

    table = "instanceConfiguration"

    def __init__(self,
                 sessionId,
                 kinectHost,
                 kinectPort,
                 cameraHost,
                 cameraPort,
                 topLeftX=None,
                 topLeftY=None,
                 topRightX=None,
                 topRightY=None,
                 bottomRightX=None,
                 bottomRightY=None,
                 bottomLeftX=None,
                 bottomLeftY=None,
                 id=uuid.uuid4()):
        super(InstanceConfiguration, self).__init__(id=id)

        self.sessionId = sessionId
        self.kinectHost = kinectHost
        self.kinectPort = kinectPort
        self.cameraHost = cameraHost
        self.cameraPort = cameraPort
        self.topLeftX = topLeftX
        self.topLeftY = topLeftY
        self.topRightX = topRightX
        self.topRightY = topRightY
        self.bottomRightX = bottomRightX
        self.bottomRightY = bottomRightY
        self.bottomLeftX = bottomLeftX
        self.bottomLeftY = bottomLeftY
