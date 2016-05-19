from src.model.Image import Image
from src.model.Postit import Postit
from src.model.SqliteObject import SqliteObject
import src.model.processing
import uuid
import datetime
import cv2
import numpy
import math


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

    def as_object(self):
        return {
            "id": str(self.id),
            "image": self.image,
            "derivedFrom": str(self.derivedFrom),
            "derivedAt": str(self.derivedAt),
            "topLeft": {
                "x": self.canvasTopLeftX,
                "y": self.canvasTopLeftY
            },
            "topRight": {
                "x": self.canvasTopRightX,
                "y": self.canvasTopRightY
            },
            "bottomRight": {
                "x": self.canvasBottomRightX,
                "y": self.canvasBottomRightY
            },
            "bottomLeft": {
                "x": self.canvasBottomLeftX,
                "y": self.canvasBottomLeftY
            },
        }

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
        image = self.get_image().get_image_array()
        if image is None:
            return None
        print(image.shape)
        return src.model.processing.four_point_transform(image, self.get_canvas_corner_points())

    def get_canvas_corner_points(self):
        return numpy.array([
            (self.canvasTopLeftX, self.canvasTopLeftY),
            (self.canvasTopRightX, self.canvasTopRightY),
            (self.canvasBottomRightX, self.canvasBottomRightY),
            (self.canvasBottomLeftX, self.canvasBottomLeftY)
        ])

    def get_canvas_unkeystoned(self):
        imgClass = self.get_image()

        if imgClass is None:
            return None
        else:
            image = imgClass.get_image_array()
            print(self.canvasTopLeftY)
            print(self.canvasBottomRightY)
            print(self.canvasTopLeftX)
            print(self.canvasBottomRightX)
            return image[self.canvasTopLeftY:self.canvasBottomRightY, self.canvasTopLeftX:self.canvasBottomRightX]

    def find_postits(self,
                     min_postit_area=5000,
                     max_postit_area=40000,
                     len_tolerence=0.4,
                     min_colour_thresh=64,
                     max_colour_thresh=200,
                     save_postits=True):

        found_postits = []
        canvas_image = self.get_canvas_keystoned()

        # Finding postits is based on saturation levels, first the image must be converted to HSV format
        hsv_image = cv2.cvtColor(canvas_image.copy(), cv2.COLOR_BGR2HSV)
        satthresh = 120 # CONST
        # All pixels with a saturation below threshold are set to black
        hsv_image[numpy.where((hsv_image < [255, satthresh, 255]).all(axis=2))] = [0, 0, 0]
        hsv_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        # All pixels below brightness threshold set to black
        # to remove any lines that have some saturation from reflections
        hsv_image[numpy.where((hsv_image < [100, 100, 100]).all(axis=2))] = [0, 0, 0]
        # Convert image to grayscale and then canny filter and get contour
        gray_img = cv2.cvtColor(hsv_image, cv2.COLOR_BGR2GRAY)
        edge_gray = cv2.Canny(gray_img, 1, 30)
        (_, contours, _) = cv2.findContours(edge_gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        postitPts = []
        postitImages = []
        postitPos = []

        for c in contours:
            box = cv2.boxPoints(cv2.minAreaRect(c))
            box = numpy.int0(box)
            # Check the area of the postits to see if they fit within the expected range
            if (cv2.contourArea(box) > min_postit_area) and (cv2.contourArea(box) < max_postit_area):
                length = math.hypot(box[0, 0] - box[1, 0], box[0, 1] - box[1, 1])
                height = math.hypot(box[2, 0] - box[1, 0], box[2, 1] - box[1, 1])
                # Check to see how similar the lengths are as a measure of squareness
                if length * (2 - len_tolerence) < length + height < length * (2 + len_tolerence):
                    rectangle = cv2.boundingRect(c)
                    flat_contour = c.flatten()
                    # Create arrays for finding the corners of the postits
                    canvx = numpy.zeros([int(len(flat_contour) / 2), 1])
                    canvy = numpy.zeros([int(len(flat_contour) / 2), 1])
                    l1 = numpy.zeros(int(len(flat_contour) / 2))
                    l2 = numpy.zeros(int(len(flat_contour) / 2))
                    l3 = numpy.zeros(int(len(flat_contour) / 2))
                    l4 = numpy.zeros(int(len(flat_contour) / 2))

                    for i in range(0, len(flat_contour), 2):
                        canvx[int(i / 2)] = flat_contour[i]
                        canvy[int(i / 2)] = flat_contour[i + 1]

                    xmax = numpy.max(canvx)
                    ymax = numpy.max(canvy)
                    xmin = numpy.min(canvx)
                    ymin = numpy.min(canvy)

                    for idx in range(0, len(canvx)):
                        lx = ((canvx[idx] - xmin) / (xmax - xmin))
                        ly = ((canvy[idx] - ymin) / (ymax - ymin))
                        # Score x and y relative to range
                        l1[idx] = lx + ly
                        l2[idx] = (1 - lx) + ly
                        l3[idx] = lx + (1 - ly)
                        l4[idx] = (1 - lx) + (1 - ly)

                    max1 = numpy.argmax(l1)
                    max2 = numpy.argmax(l2)
                    max3 = numpy.argmax(l3)
                    max4 = numpy.argmax(l4)
                    postit_pts = [(canvx[max1][0], canvy[max1][0]),
                                  (canvx[max2][0], canvy[max2][0]),
                                  (canvx[max3][0], canvy[max3][0]),
                                  (canvx[max4][0], canvy[max4][0])]
                    # Crop and transform image based on points
                    postitimg = src.model.processing.four_point_transform(canvas_image, numpy.array(postit_pts))
                    postitPts.append(numpy.array(postit_pts))
                    postitImages.append(postitimg)
                    postitPos.append(rectangle)

        for idx, postit_image in enumerate(postitImages):
            # Calculate average postit colour in order to guess the colour of the postit
            gray_image = cv2.cvtColor(postit_image, cv2.COLOR_BGR2GRAY)
            red_total = green_total = blue_total = 0
            (width, height, depth) = postit_image.shape
            for y in range(height):
                for x in range(width):
                    if min_colour_thresh < gray_image[x, y] < max_colour_thresh:
                        b, g, r = postit_image[x, y]
                        red_total += r
                        green_total += g
                        blue_total += b

            count = width * height

            red_average = red_total / count
            green_average = green_total / count
            blue_average = blue_total / count

            guessed_colour = src.model.processing.guess_colour(red_average, green_average, blue_average)
            # Only if a postit colour valid create a postit
            if guessed_colour is not None:
                postitPts = src.model.processing.order_points(postitPts[idx])

                postit = Postit(topLeftX=postitPts[0][0],
                                topLeftY=postitPts[0][1],
                                topRightX=postitPts[1][0],
                                topRightY=postitPts[1][1],
                                bottomRightX=postitPts[2][0],
                                bottomRightY=postitPts[2][1],
                                bottomLeftX=postitPts[3][0],
                                bottomLeftY=postitPts[3][1],
                                colour=guessed_colour,
                                canvas=self.get_id())

                if save_postits:
                    postit.create(self.database)

                found_postits.append(postit)

        return found_postits
