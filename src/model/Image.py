import datetime
import uuid
import cv2
import os
import requests
import numpy
from src.model.SqliteObject import SqliteObject
import pytz
import src.model.processing


class Image(SqliteObject):

    properties = ["id", "timestamp"]
    table = "images"

    def __init__(self,
                 npArray=None,
                 id=uuid.uuid4(),
                 timestamp=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC),
                 database=None):
        super().__init__(id=id,
                         database=database)
        self.image = npArray
        self.timestamp = timestamp

    @staticmethod
    def from_uri(uri='http://localhost:8080'):
        response = requests.get(uri)

        if response.status_code == 200:
            nparray = numpy.asarray(bytearray(response.content), dtype="uint8")
            return Image(id=uuid.uuid4(),
                         npArray=cv2.imdecode(nparray, cv2.IMREAD_COLOR))
        else:
            print(response.status_code)
            print(response.json())
            return None

    def get_image_array(self):
        if not self.image:
            self.image = cv2.imread(self.get_image_path())

        return self.image

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def create(self, database=None):
        super(Image, self).create(database=database)
        cv2.imwrite(self.get_image_path(), self.image)
        return self

    def delete(self, database=None):
        super(Image, self).delete(database=database)
        os.remove(self.get_image_path())
        return self

    def get_image_path(self):
        return Image.get_image_directory(self.id)

    @staticmethod
    def get_image_directory(id):
        base_path = os.path.join(os.getcwd(), './server/static/images')
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        path = os.path.join(base_path, str(id) + ".jpg")
        return path

    @staticmethod
    def focus_camera(uri):
        uri += '/focus'
        print('Focusing Camera with URI ' + str(uri))
        response = requests.get(uri)
        print(response.status_code)
        return response.status_code == 204

    @staticmethod
    def get_camera_properties(uri):
        uri += "/properties"
        print('Getting Camera Properties from URI ' + str(uri))
        response = requests.get(uri)

        if response.status_code == 200:
            print('Got Good response from camera!')
            return response.json()
        else:
            print(response.status_code)
            print(response.json())
            return None

    @staticmethod
    def set_camera_properties(uri, properties):
        uri += "/properties"
        print('Setting Camera Properties with URI ' + str(uri))

        response = requests.post(uri, properties)

        print(response.status_code)

        return response.status_code == 200

    def find_canvas(self, save_canvas_to_db=True):
        """
        Attempt to find bounds to a canvas in the image, using the brightest rectangular-like
        area available. This method returns a tuple of x,y points in the order
        (topLeft, topRight, bottomRight, bottomLeft)

        :param save_canvas_to_db boolean if the returned canvas object should be saved to the database
        before being returned (default True)
        """

        # Grab a black+white smooth image
        smooth_img = src.model.processing.grayscale_smooth(self.get_image_array())
        _, threshold_board = cv2.threshold(smooth_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # grab a list of contours on the board
        (_, board_contours, _) = cv2.findContours(threshold_board, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(c) for c in board_contours]

        # get the biggest contour area
        max_index = numpy.argmax(areas)
        canvas_contour = board_contours[max_index]
        fcanvas_contours = canvas_contour.flatten()

        canvx = numpy.zeros([int(len(fcanvas_contours) / 2), 1])
        canvy = numpy.zeros([int(len(fcanvas_contours) / 2), 1])

        # extract corner points
        topLeft = numpy.zeros(int(len(fcanvas_contours) / 2))
        topRight = numpy.zeros(int(len(fcanvas_contours) / 2))
        bottomRight = numpy.zeros(int(len(fcanvas_contours) / 2))
        bottomLeft = numpy.zeros(int(len(fcanvas_contours) / 2))

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

            topLeft[n]     = (1 - lx) + (1 - ly)
            topRight[n]    = (1 - lx) + ly
            bottomRight[n] = lx + ly
            bottomLeft[n]  = lx + (1 - ly)

        maxTopLeft = numpy.argmax(topLeft)
        maxTopRight = numpy.argmax(topRight)
        maxBottomRight = numpy.argmax(bottomRight)
        maxBottomLeft = numpy.argmax(bottomLeft)

        # TODO: check bounds are not all equal
        # TODO: fail should reutnr whole image as canvas, npt throw exception

        from src.model.Canvas import Canvas
        canvas = Canvas(image=self.get_id(),
                        canvasTopLeftX=canvx[maxTopLeft][0],
                        canvasTopLeftY=canvy[maxTopLeft][0],
                        canvasTopRightX=canvx[maxTopRight][0],
                        canvasTopRightY=canvy[maxTopRight][0],
                        canvasBottomRightX=canvx[maxBottomRight][0],
                        canvasBottomRightY=canvy[maxBottomRight][0],
                        canvasBottomLeftX = canvx[maxBottomLeft][0],
                        canvasBottomLeftY = canvy[maxBottomLeft][0])

        if save_canvas_to_db:
            canvas.create(self.database)

        return canvas
