import uuid
from src.model.SqliteObject import SqliteObject
import numpy


class InstanceConfiguration(SqliteObject):
    properties = [
        "id",
        "sessionId",
        "userId",
        "topLeftX",
        "topLeftY",
        "topRightX",
        "topRightY",
        "bottomRightX",
        "bottomRightY",
        "bottomLeftX",
        "bottomLeftY",
        "cameraHost",
        "kinectHost",
        "cameraPort",
        "kinectPort"
    ]

    table = "instanceConfiguration"

    def __init__(self,
                 sessionId,
                 userId,
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
        self.userId = userId
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

    def as_object(self):
        return {
            "id": str(self.id),
            "userId": self.userId,
            "sessionId": self.sessionId,
            "kinect": {
                "host": self.kinectHost,
                "port": self.kinectPort
            },
            "camera": {
                "host": self.cameraHost,
                "port": self.cameraPort
            },
            "topLeft": {
                "x": self.topLeftX,
                "y": self.topLeftY
            },
            "topRight": {
                "x": self.topRightX,
                "y": self.topRightY
            },
            "bottomRight": {
                "x": self.bottomRightX,
                "y": self.bottomRightY
            },
            "bottomLeft": {
                "x": self.bottomLeftX,
                "y": self.bottomLeftY
            }
        }

    def get_projection_corner_points(self):

        return numpy.array([
            (self.topLeftX, self.topLeftY),
            (self.topRightX, self.topRightY),
            (self.bottomRightX, self.bottomRightY),
            (self.bottomLeftX, self.bottomLeftY),
        ])
