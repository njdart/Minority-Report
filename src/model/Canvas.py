from src.model.Image import Image
from src.model.Postit import Postit
from src.model.SqliteObject import SqliteObject
import uuid
import datetime


class Canvas(SqliteObject):
    """
    A Canvas object relating an image to it's canvas bounds
    """

    properties = [
        "id",
        "image",
        "derivedFrom",
        "derivedAt",
        "canvasTopLeftX",
        "canvasTopLeftY",
        "canvasTopRightX",
        "canvasTopRightY",
        "canvasBottomLeftX",
        "canvasBottomLeftY",
        "canvasBottomRightX",
        "canvasBottomRightY"
    ]

    table = "canvases"

    def __init__(self,
                 image,
                 canvasTopLeftX=None,
                 canvasTopLeftY=None,
                 canvasTopRightX=None,
                 canvasTopRightY=None,
                 canvasBottomLeftX=None,
                 canvasBottomLeftY=None,
                 canvasBottomRightX=None,
                 canvasBottomRightY=None,
                 canvasBounds=None,
                 id=uuid.uuid4(),
                 postits=[],
                 connections=[],
                 derivedFrom=None,
                 derivedAt=datetime.datetime.now()):
        """
        :param image OpenCV Numpy array
        :param canvasBounds list of (x, y) tuples in the order [topLeft, topRight, bottomRight, bottomLeft]
        :param id UUID v4
        :param postits list of postit objects or UUID v4s
        :param connections list of (postit/postitUUID, postit/postitUUID) tuples
        :param derivedFrom canvas object or ID this object derives from
        """
        super(Canvas, self).__init__(id=id)
        self.image = image
        if canvasBounds is not None:
            canvasTopLeft = canvasBounds[0]
            self.canvasTopLeftX = int(canvasTopLeft[0])
            self.canvasTopLeftY = int(canvasTopLeft[1])

            canvasTopRight = canvasBounds[1]
            self.canvasTopRightX = int(canvasTopRight[0])
            self.canvasTopRightY = int(canvasTopRight[1])

            canvasBottomRight = canvasBounds[2]
            self.canvasBottomRightX = int(canvasBottomRight[0])
            self.canvasBottomRightY = int(canvasBottomRight[1])

            canvasBottomLeft = canvasBounds[3]
            self.canvasBottomLeftX = int(canvasBottomLeft[0])
            self.canvasBottomLeftY = int(canvasBottomLeft[1])

        else:
            self.canvasTopLeftX = int(canvasTopLeftX)
            self.canvasTopLeftY = int(canvasTopLeftY)
            self.canvasTopRightX = int(canvasTopRightX)
            self.canvasTopRightY = int(canvasTopRightY)
            self.canvasBottomRightX = int(canvasBottomRightX)
            self.canvasBottomRightY = int(canvasBottomRightY)
            self.canvasBottomLeftX = int(canvasBottomLeftX)
            self.canvasBottomLeftY = int(canvasBottomLeftY)

        self.postits = postits
        self.connections = connections
        self.derivedFrom = derivedFrom
        self.derivedAt = derivedAt

    def get_postit(self, id):
        """
        get a postit by it's id"""
        for postit in self.postits:
            if type(postit) == int and postit == id:
                return Postit.get(id)
            elif postit.get_id() == id:
                return postit
        return None

    def add_connection(self, start, end):
        self.connections.append((start, end))

    def get_image(self):
        if type(self.image) == str:
            return Image.get(self.image)
        else:
            return self.image

    def get_canvas_keystoned(self):
        raise Exception('Not Implemented ... Josh?')

    def get_canvas_bounds(self):
        return ((self.canvasTopLeftX, self.canvasTopLeftY),
                (self.canvasBottomRightX, self.canvasBottomRightY))

    def get_canvas_unkeystoned(self):
        imgClass = self.get_image()

        if imgClass is None:
            return None
        else:
            image = imgClass.get_image()
            print(self.canvasTopLeftY)
            print(self.canvasBottomRightY)
            print(self.canvasTopLeftX)
            print(self.canvasBottomRightX)
            return image[self.canvasTopLeftY:self.canvasBottomRightY, self.canvasTopLeftX:self.canvasBottomRightX]
