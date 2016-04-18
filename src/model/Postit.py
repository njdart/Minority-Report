import cv2
import uuid
import numpy as np
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
                 pnt1X,
                 pnt1Y,
                 pnt2X,
                 pnt2Y,
                 pnt3X,
                 pnt3Y,
                 pnt4X,
                 pnt4Y,
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
        self.pnt1X = pnt1X
        self.pnt1Y = pnt1Y
        self.pnt2X = pnt2X
        self.pnt2Y = pnt2Y
        self.pnt3X = pnt3X
        self.pnt3Y = pnt3Y
        self.pnt4X = pnt4X
        self.pnt4Y = pnt4Y
        self.colour = colour
        self.physical = physical
        self.canvas = canvas

    def get_position(self):
        return (self.realX, self.realY)

    def get_size(self):
        return (self.width, self.height)

    def get_points(self):
        return [(self.pnt1X, self.pnt1Y),
                (self.pnt2X, self.pnt2Y),
                (self.pnt3X, self.pnt3Y),
                (self.pnt4X, self.pnt4Y)]

    def get_color(self):
        return self.colour

    def set_physical(self, state=False):
        self.physical = state

    def get_descriptors(self,canvasImage):
        sift = cv2.xfeatures2d.SIFT_create()
        postit = self.getImage(canvasImage)
        gray = cv2.cvtColor(postit, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = sift.detectAndCompute(gray,None)
        return descriptors

    def get_canvas(self):
        #if type(self.canvas) == uuid.UUID:
        #    return self.databaseHandler.get_canvas(self.canvas)
        #else:
            return self.canvas

    def get_postit_image(self, canvasImage):
        postitPoints = [(self.pnt1X, self.pnt1Y),
                        (self.pnt2X, self.pnt2Y),
                        (self.pnt3X, self.pnt3Y),
                        (self.pnt4X, self.pnt4Y)]

        postit = self.four_point_transform(canvasImage, np.array(postitPoints))
        #postit = canvasImage[self.realY:(self.realY+self.height), self.realX:(self.realX+self.width)]
        return postit

    def four_point_transform(self, image, pts):
        # obtain a consistent order of the points and unpack them
        # individually
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype = "float32")

        # compute the perspective transform matrix and then apply it
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        # return the warped image
        return warped

    def order_points(self, pts):
        # initialzie a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype = "float32")

        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # return the ordered coordinates
        return rect

    def update_postit(self,
                x,
                y,
                width,
                height,
                pnt1X,
                pnt1Y,
                pnt2X,
                pnt2Y,
                pnt3X,
                pnt3Y,
                pnt4X,
                pnt4Y,
                colour,
                canvas,
                physical):

        self.realX = x
        self.realY = y
        self.width = width
        self.height = height
        self.pnt1X = pnt1X
        self.pnt1Y = pnt1Y
        self.pnt2X = pnt2X
        self.pnt2Y = pnt2Y
        self.pnt3X = pnt3X
        self.pnt3Y = pnt3Y
        self.pnt4X = pnt4X
        self.pnt4Y = pnt4Y
        self.colour = colour
        self.physical = physical
        self.canvas = canvas

