import cv2
import uuid
import numpy
import src.model.processing
from src.model.SqliteObject import SqliteObject


class Postit(SqliteObject):
    """
    Represents a postit in a canvas
    """

    properties = [
        "id",
        "canvas",
        "topLeftX",
        "topLeftY",
        "topRightX",
        "topRightY",
        "bottomRightX",
        "bottomRightY",
        "bottomLeftX",
        "bottomLeftY",
        "colour"
    ]

    table = "postits"

    def __init__(self,
                 topLeftX,
                 topLeftY,
                 topRightX,
                 topRightY,
                 bottomRightX,
                 bottomRightY,
                 bottomLeftX,
                 bottomLeftY,
                 colour,
                 canvas,
                 physical=True,
                 id=uuid.uuid4(),
                 database=None):
        super(Postit, self).__init__(id=id,
                                     database=database)
        self.topLeftX = int(topLeftX)
        self.topLeftY = int(topLeftY)
        self.topRightX = int(topRightX)
        self.topRightY = int(topRightY)
        self.bottomRightX = int(bottomRightX)
        self.bottomRightY = int(bottomRightY)
        self.bottomLeftX = int(bottomLeftX)
        self.bottomLeftY = int(bottomLeftY)
        self.colour = colour
        self.physical = physical
        self.canvas = canvas

    def get_position(self):
        return (self.topLeftX, self.topLeftY)

    def get_image(self):
        canvas = self.get_canvas()
        if canvas is None:
            return None

        image = canvas.get_image()
        if image is None:
            return None

        return image

    def as_object(self):
        return {
            "id": str(self.id),
            "canvas": str(self.canvas),
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

    def get_image_keystoned(self):
        image = self.get_image()

        if image is None:
            return None

        return src.model.processing.four_point_transform(image, self.get_corner_points())

    def get_corner_points(self):
        return numpy.array([
            (self.topLeftX, self.topLeftY),
            (self.topRightX, self.topRightY),
            (self.bottomRightX, self.bottomRightY),
            (self.bottomLeftX, self.bottomLeftY)
        ])

    def get_color(self):
        return self.colour

    def set_physical(self, state=False):
        self.physical = state

    def get_descriptors(self, canvasImage):
        sift = cv2.xfeatures2d.SIFT_create()
        postit = self.getImage(canvasImage)
        gray = cv2.cvtColor(postit, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = sift.detectAndCompute(gray, None)
        return descriptors

    def get_canvas(self):
        if type(self.canvas) is uuid.UUID or type(self.canvas) is str:
            from src.model.Canvas import Canvas
            canvas = Canvas.get(self.canvas)
            if canvas is None:
                return None
            self.canvas = canvas

        return self.canvas

    def get_postit_image(self):
        canvas = self.get_canvas().get_canvas_keystoned()

        if canvas is None:
            return None

        return src.model.processing.four_point_transform(canvas, self.get_corner_points())

    def update_postit(self,
                      x,
                      y,
                      width,
                      height,
                      keystone1X,
                      keystone1Y,
                      keystone2X,
                      keystone2Y,
                      keystone3X,
                      keystone3Y,
                      keystone4X,
                      keystone4Y,
                      colour,
                      canvas,
                      physical):

        self.realX = x
        self.realY = y
        self.width = width
        self.height = height
        self.keystone1X = keystone1X
        self.keystone1Y = keystone1Y
        self.keystone2X = keystone2X
        self.keystone2Y = keystone2Y
        self.keystone3X = keystone3X
        self.keystone3Y = keystone3Y
        self.keystone4X = keystone4X
        self.keystone4Y = keystone4Y
        self.colour = colour
        self.physical = physical
        self.canvas = canvas
