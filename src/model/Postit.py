import cv2
import uuid
from src.model.SqliteObject import SqliteObject


class Postit(SqliteObject):
    """
    Represents a postit in a canvas
    """

    def __init__(self,
                 x,
                 y,
                 width,
                 height,
                 colour,
                 canvas,
                 physical=True,
                 id=uuid.uuid4(),
                 databaseHandler=None):
        super(Postit, self).__init__(id=id,
                                     properties=[
                                         "id",
                                         "canvas",
                                         "height",
                                         "width",
                                         "realX",
                                         "realY",
                                         "colour"
                                     ],
                                     table="postits",
                                     databaseHandler=databaseHandler)
        self.realX = x
        self.realY = y
        self.width = width
        self.height = height
        self.colour = colour
        self.physical = self.physical
        self.colour = colour
        self.physical = physical
        self.canvas = canvas

    def get_position(self):
        return (self.realX, self.realY)

    def get_size(self):
        return (self.width, self.height)

    def get_color(self):
        return self.colour

    def set_physical(self, state=False):
        self.physical = state

    def get_descriptors(self, canvasImage):
        sift = cv2.xfeatures2d.SIFT_create()
        postit = self.getImage(canvasImage)
        gray = cv2.cvtColor(postit, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = sift.detectAndCompute(gray,None)
        return descriptors

    def get_postit_image(self):
        pass

    def get_canvas(self):
        if type(self.canvas) == uuid.UUID:
            return self.databaseHandler.get_canvas(self.canvas)
        else:
            return self.canvas

    def get_postit_image(self, scaleWidth, scaleHeight):
        raise Exception('Not Implemented ... Josh?')
        #postit = canvasImage[self.location[1]:(self.location[1]+self.size[1]), self.location[0]:(self.location[0]+self.size[0])]
        #return postit
