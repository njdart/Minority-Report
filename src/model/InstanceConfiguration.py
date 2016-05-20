import uuid
from src.model.SqliteObject import SqliteObject
import numpy
import cv2
import src.model.processing
from src.model.Image import Image

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
            (int(round(float(self.topLeftX))), int(round(float(self.topLeftY)))),
            (int(round(float(self.topRightX))), int(round(float(self.topRightY)))),
            (int(round(float(self.bottomRightX))), int(round(float(self.bottomRightY)))),
            (int(round(float(self.bottomLeftX))), int(round(float(self.bottomLeftY))))
        ])

    def calibrate(self):
        cameraUri = "http://{}:{}".format(self.cameraHost, self.cameraPort)
        print('Getting Calibration Image from URI {}'.format(cameraUri))
        calib_image = Image.from_uri(self.id, cameraUri)
        calib_image_array = calib_image.get_image_array()
        bin_image = cv2.cvtColor(src.model.processing.binarize(calib_image_array), cv2.COLOR_RGB2GRAY)
        (__, board_contours, __) = cv2.findContours(bin_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(c) for c in board_contours]
        max_index = numpy.argmax(areas)
        canvas_contour = board_contours[max_index]
        self.simpleBounds = cv2.boundingRect(canvas_contour)
        fcanvas_contours = canvas_contour.flatten()
        canvx = numpy.zeros([int(len(fcanvas_contours) / 2), 1])
        canvy = numpy.zeros([int(len(fcanvas_contours) / 2), 1])
        l1 = numpy.zeros(int(len(fcanvas_contours) / 2))
        l2 = numpy.zeros(int(len(fcanvas_contours) / 2))
        l3 = numpy.zeros(int(len(fcanvas_contours) / 2))
        l4 = numpy.zeros(int(len(fcanvas_contours) / 2))
        for i in range(0, len(fcanvas_contours), 2):
            canvx[int(i / 2)] = fcanvas_contours[i]
            canvy[int(i / 2)] = fcanvas_contours[i + 1]
        xmax = numpy.max(canvx)
        ymax = numpy.max(canvy)
        xmin = numpy.min(canvx)
        ymin = numpy.min(canvy)
        for n in range(0, len(canvx)):
            lx = ((canvx[n] - xmin) / (xmax - xmin))
            ly = ((canvy[n] - ymin) / (ymax - ymin))
            l1[n] = (1 - lx) + (1 - ly)
            l2[n] = lx + (1 - ly)
            l3[n] = lx + ly
            l4[n] = (1 - lx) + ly
        max1 = numpy.argmax(l1)
        max2 = numpy.argmax(l2)
        max3 = numpy.argmax(l3)
        max4 = numpy.argmax(l4)
        self.topLeftX = canvx[max1][0]
        self.topLeftY = canvy[max1][0]
        self.topRightX = canvx[max2][0]
        self.topRightY = canvy[max2][0]
        self.bottomRightX = canvx[max3][0]
        self.bottomRightY = canvy[max3][0]
        self.bottomLeftX = canvx[max4][0]
        self.bottomLeftY = canvy[max4][0]
        return self
