import uuid
from src.model.SqliteObject import SqliteObject
from src.server import databaseHandler
import numpy
import cv2
import src.model.processing
from src.model.Image import Image
import json
import requests

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
                 id=None,
                 kinectID=None):
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
        self.calibSuccess = True

        self.kinectID = kinectID if kinectID is not None else uuid.uuid4()

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
            },
            "calibSuccess": self.calibSuccess
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

        kinectCalibUri = "http://{}:{}/calibrate".format(self.kinectHost, self.kinectPort)
        print("Getting Kinect calibration image from URI {}".format(kinectCalibUri))

        self.calibSuccess = True

        calib_image = Image.from_uri(self.id, cameraUri)
        if calib_image == None:
            print("Camera calibration failed")
            self.calibSuccess = False

        kinect_calib_image = Image.from_uri(self.id, kinectCalibUri)
        if kinect_calib_image == None:
            print("Kinect calibration failed")
            self.calibSuccess = False

        def getcanvascoords(img):
            # Do a load of Josh magic to get the canvas coordinates.
            calib_image_array = img.get_image_array()
            bin_image = cv2.cvtColor(src.model.processing.binarize(calib_image_array), cv2.COLOR_RGB2GRAY)
            cv2.imwrite("debug.png",cv2.resize(bin_image, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA))
            (__, board_contours, __) = cv2.findContours(bin_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            areas = [cv2.contourArea(c) for c in board_contours]
            max_index = numpy.argmax(areas)
            canvas_contour = board_contours[max_index]
            # self.simpleBounds = cv2.boundingRect(canvas_contour)
            bounds = cv2.boundingRect(canvas_contour)
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
            return (canvx, canvy, bounds, max1, max2, max3, max4)

        # Josh magic on the camera image...
        if calib_image != None:
            (canvx, canvy, bounds, max1, max2, max3, max4) = getcanvascoords(calib_image)
            self.topLeftX = canvx[max1][0]
            self.topLeftY = canvy[max1][0]
            self.topRightX = canvx[max2][0]
            self.topRightY = canvy[max2][0]
            self.bottomRightX = canvx[max3][0]
            self.bottomRightY = canvy[max3][0]
            self.bottomLeftX = canvx[max4][0]
            self.bottomLeftY = canvy[max4][0]
            self.simpleBounds = bounds
            print("Calibrated from camera image")

        if kinect_calib_image != None:
            # Josh magic on the Kinect image...
            (canvx, canvy, bounds, max1, max2, max3, max4) = getcanvascoords(kinect_calib_image)
            print("Calibrated from Kinect image")
            # and send it off
            payload = {
                "points": [
                    [canvx[max1][0], canvy[max1][0]],
                    [canvx[max2][0], canvy[max2][0]],
                    [canvx[max3][0], canvy[max3][0]],
                    [canvx[max4][0], canvy[max4][0]]
                ],
                "instanceID": str(self.kinectID)
            }
            try:
                response = requests.post("http://{}:{}/calibrate".format(self.kinectHost, self.kinectPort), data=json.dumps(payload))
                print("Sent calibration data to Kinect server application")
                try:
                    if json.loads(response.text)["instanceID"] != str(self.kinectID):
                        print("WARNING: Kinect did not echo back its ID...")
                    else:
                        print("Kinect echoed back successfully.")
                except Exception as e:
                    print("WARNING: Kinect did not send back coherent echo...", e)
            except requests.exceptions.RequestException as e:
                print("Failed to send calibration data to Kinect:", e)

        return self

    def get_latest_image_id(self):
        if self.database:
            c = self.database.cursor()
        else:
            c = databaseHandler().get_database().cursor()

        query = 'SELECT (id) FROM images WHERE instanceConfigurationId="{}" ORDER BY datetime(timestamp) DESC LIMIT 1;'.format(self.id)

        c.execute(query)
        data = c.fetchone()

        if data is None:
            return None

        return data[0]
