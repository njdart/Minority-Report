from src.model.SqliteObject import SqliteObject
import uuid
import datetime


class Canvas(SqliteObject):
    """
    A Canvas object relating an image to it's canvas bounds
    """

    def __init__(self,
                 image,
                 canvasBounds,
                 id=uuid.uuid4(),
                 postits=[],
                 derivedFrom=None,
                 derivedAt=datetime.datetime.now(),
                 databaseHandler=None):
        """
        :param image OpenCV Numpy array
        :param canvasBounds list of (x, y) tuples in the order [topLeft, topRight, bottomRight, bottomLeft]
        :param id UUID v4
        :param postits list of postit objects or UUID v4s
        :param derivedFrom canvas object or ID this object derives from
        """
        super(Canvas, self).__init__(id=id,
                                     properties=[
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
                                     ],
                                     table="canvas",
                                     databaseHandler=databaseHandler)
        self.image = image

        canvasTopLeft = canvasBounds[0]
        self.canvasTopLeftX = canvasTopLeft[0]
        self.canvasTopLeftY = canvasTopLeft[1]

        canvasTopRight = canvasBounds[1]
        self.canvasTopRightX = canvasTopRight[0]
        self.canvasTopRightY = canvasTopRight[1]

        canvasBottomRight = canvasBounds[2]
        self.canvasBottomRightX = canvasBottomRight[0]
        self.canvasBottomRightY = canvasBottomRight[1]

        canvasBottomLeft = canvasBounds[3]
        self.canvasBottomLeftX = canvasBottomLeft[0]
        self.canvasBottomLeftY = canvasBottomLeft[1]

        self.postits = postits
        self.derivedFrom = derivedFrom
        self.derivedAt = derivedAt

    def get_postit(self, id):
        """
        get a postit by it's id"""
        for postit in self.postits:
            if type(postit) == int and postit == id:
                return self.databaseHandler.get_postit(id)
            elif postit.get_id() == id:
                return postit
        return None

    def get_image(self):
        return self.image

    def get_canvas_keystoned(self):
        raise Exception('Not Implemented ... Josh?')

    def get_canvas_unkeystoned(self):
        return self.image[self.canvasTopLeftY:self.canvasBottomRightY, self.canvasTopLeftX:self.canvasBottomRightX]
