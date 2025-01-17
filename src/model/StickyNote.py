import cv2
import uuid
import numpy
import src.model.processing
from src.model.SqliteObject import SqliteObject


class StickyNote(SqliteObject):
    """
    Represents a stickyNote in a canvas
    """

    properties = [
        "id",
        "canvas",
        "physicalFor",
        "topLeftX",
        "topLeftY",
        "topRightX",
        "topRightY",
        "bottomRightX",
        "bottomRightY",
        "bottomLeftX",
        "bottomLeftY",
        "displayPosX",
        "displayPosY",
        "colour",
        "image"
    ]

    table = "stickyNotes"

    def __init__(self,
                 canvas,
                 topLeftX,
                 topLeftY,
                 topRightX,
                 topRightY,
                 bottomRightX,
                 bottomRightY,
                 bottomLeftX,
                 bottomLeftY,
                 displayPosX,
                 displayPosY,
                 colour,
                 image,
                 physicalFor=None,
                 id=None,
                 database=None):
        super(StickyNote, self).__init__(id=id,
                                     database=database)
        self.canvas = canvas
        self.topLeftX = int(topLeftX)
        self.topLeftY = int(topLeftY)
        self.topRightX = int(topRightX)
        self.topRightY = int(topRightY)
        self.bottomRightX = int(bottomRightX)
        self.bottomRightY = int(bottomRightY)
        self.bottomLeftX = int(bottomLeftX)
        self.bottomLeftY = int(bottomLeftY)
        self.displayPosX = int(displayPosX)
        self.displayPosY = int(displayPosY)
        self.colour = colour
        self.physicalFor = physicalFor
        self.image = image

    def get_position(self):
        return (self.topLeftX, self.topLeftY)

    def get_image(self):
        if type(self.image) is uuid.UUID or type(self.image) is str:
            from src.model.Image import Image
            image = Image.get(self.image)
            if image is None:
                return None
            self.image = image

        return self.image

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
            },
            "displayPos": {
                "x": self.displayPosX,
                "y": self.displayPosY
            },
            "physicalFor": str(self.physicalFor)
        }

    def get_image_keystoned(self):
        image = self.get_image()

        if image is None:
            return None

        return src.model.processing.four_point_transform(image.get_image_projection(), self.get_corner_points())

    def get_image_binarized(self):
        image = self.get_image_keystoned()
        image = image[7:image.shape[0]-7, 7:image.shape[1]-7]
        stickyNoteImage = src.model.processing.binarize(image, lightest=False)
        if self.colour == "ORANGE":
            stickyNoteImage[numpy.where((stickyNoteImage > [0, 0, 0]).all(axis=2))] = [26, 160, 255]
        elif self.colour == "YELLOW":
            stickyNoteImage[numpy.where((stickyNoteImage > [0, 0, 0]).all(axis=2))] = [93, 255, 237]
        elif self.colour == "BLUE":
            stickyNoteImage[numpy.where((stickyNoteImage > [0, 0, 0]).all(axis=2))] = [255, 200, 41]
        elif self.colour == "MAGENTA":
            stickyNoteImage[numpy.where((stickyNoteImage > [0, 0, 0]).all(axis=2))] = [182, 90, 255]
        return stickyNoteImage

    def get_corner_points(self):
        return numpy.array([
            (int(round(float(self.topLeftX))), int(round(float(self.topLeftY)))),
            (int(round(float(self.topRightX))), int(round(float(self.topRightY)))),
            (int(round(float(self.bottomRightX))), int(round(float(self.bottomRightY)))),
            (int(round(float(self.bottomLeftX))), int(round(float(self.bottomLeftY))))
        ])

    def get_color(self):
        return self.colour

    def set_physical(self, state=False):
        self.physical = state

    def get_descriptors(self):
        orb = cv2.ORB_create(scaleFactor=1.2,
                             nlevels=8,
                             edgeThreshold=1,
                             firstLevel=0,
                             WTA_K=2,
                             scoreType=cv2.ORB_HARRIS_SCORE,
                             patchSize=31)
        binary_stickyNote_image = self.get_image_binarized()
        __, descriptors = orb.detectAndCompute(binary_stickyNote_image, None)
        return descriptors

    def get_canvas(self):
        if type(self.canvas) is uuid.UUID or type(self.canvas) is str:
            from src.model.Canvas import Canvas
            canvas = Canvas.get(self.canvas)
            if canvas is None:
                return None
            self.canvas = canvas

        return self.canvas

    def set_display_pos(self, newXpos, newYpos):
        self.displayPosX = newXpos
        self.displayPosY = newYpos
        return self

    def get_stickyNote_image(self):
        from src.model.Image import Image
        image = Image.get(self.image)

        if image is None:
            return None

        return src.model.processing.four_point_transform(image.get_image_projection(), self.get_corner_points())

    def update_stickyNote(self,
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
