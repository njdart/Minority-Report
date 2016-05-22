import os
import uuid
import cv2
import numpy
import requests
import src.model.processing
import datetime
from src.model.SqliteObject import SqliteObject


class Image(SqliteObject):

    properties = ["id", "timestamp", "instanceConfigurationId"]
    table = "images"

    def __init__(self,
                 instanceConfigurationId,
                 npArray=None,
                 id=uuid.uuid4(),
                 timestamp=datetime.datetime.now().isoformat(),
                 database=None):
        super().__init__(id=id,
                         database=database)
        self.image = npArray
        self.timestamp = timestamp
        self.instanceConfigurationId = instanceConfigurationId

    @staticmethod
    def from_uri(instanceConfigurationId, uri='http://localhost:8080'):
        print('Getting image for config id {} from {}'.format(instanceConfigurationId, uri))
        response = requests.get(uri)

        if response.status_code == 200:
            nparray = numpy.asarray(bytearray(response.content), dtype="uint8")
            return Image(id=uuid.uuid4(),
                         instanceConfigurationId=instanceConfigurationId,
                         npArray=cv2.imdecode(nparray, cv2.IMREAD_COLOR),
                         timestamp=datetime.datetime.now().isoformat())
        else:
            print(response.status_code)
            print(response.json())
            return None

    def get_image_array(self):
        if self.image is None:
            self.image = cv2.imread(self.get_image_path())

        return self.image

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def create(self, database=None):
        super(Image, self).create(database=database)
        print('Writing Image to file', self.get_image_path())
        cv2.imwrite(self.get_image_path(), self.image)
        return self

    def delete(self, database=None):
        super(Image, self).delete(database=database)
        os.remove(self.get_image_path())
        return self

    def get_image_path(self):
        return Image.get_image_directory(self.id)

    def get_image_projection(self):

        image = self.get_image_array()
        if image is None:
            print('Could not get Image Projection; image array was None')
            return None

        instanceConfiguration = self.get_instance_configuration()
        if instanceConfiguration is None:
            print('Could not get Image Projection; instance configuration was None')
            return None

        print(instanceConfiguration.get_projection_corner_points())

        return src.model.processing.four_point_transform(image, instanceConfiguration.get_projection_corner_points())

    def get_instance_configuration(self):
        from src.model.InstanceConfiguration import InstanceConfiguration
        return InstanceConfiguration.get(id=self.instanceConfigurationId)

    def get_canvas(self):
        # TODO Will return canvas objects for HUD?
        pass

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

    def find_postits(self,
                     save=True,
                     min_postit_area=5000,
                     max_postit_area=40000,
                     len_tolerence=0.4,
                     min_colour_thresh=64,
                     max_colour_thresh=200,
                     save_postits=True):

        from src.model.Postit import Postit

        found_postits = []
        canvas_image = self.get_image_projection()

        # Finding postits is based on saturation levels, first the image must be converted to HSV format
        hsv_image = cv2.cvtColor(canvas_image.copy(), cv2.COLOR_BGR2HSV)
        satthresh = 120  # CONST
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
                length = numpy.math.hypot(box[0, 0] - box[1, 0], box[0, 1] - box[1, 1])
                height = numpy.math.hypot(box[2, 0] - box[1, 0], box[2, 1] - box[1, 1])
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
        canvas_id = uuid.uuid4()
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

                postit = Postit(canvas = canvas_id,
                                topLeftX=postitPts[0][0],
                                topLeftY=postitPts[0][1],
                                topRightX=postitPts[1][0],
                                topRightY=postitPts[1][1],
                                bottomRightX=postitPts[2][0],
                                bottomRightY=postitPts[2][1],
                                bottomLeftX=postitPts[3][0],
                                bottomLeftY=postitPts[3][1],
                                displayPosX=postitPts[0][0]*(1920/canvas_image.shape[0]),
                                displayPosY=postitPts[0][1]*(1920/canvas_image.shape[0]),
                                colour=guessed_colour,
                                image=self.get_id())
                if save_postits:
                    postit.create(self.database)

                found_postits.append(postit)

        return found_postits

    def find_connections(self, postits, canvas, save=True):
        found_connections = []
        canvas_image = self.get_image_projection()
        edged = src.model.processing.edge(canvas_image)
        (_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for c in cnts:
            debug_img = canvas_image.copy()
            if cv2.arcLength(c, True) > 300:
                array = []
                for index in range(0, len(c), 10):
                    contained = False
                    for idx, ipostit in enumerate(postits):
                        rectanglearea = src.model.processing.get_area(ipostit["points"])
                        pointarea = src.model.processing.get_area((ipostit["points"][0], ipostit["points"][1], c[index][0]))\
                                    + src.model.processing.get_area((ipostit["points"][1], ipostit["points"][2], c[index][0]))\
                                    + src.model.processing.get_area((ipostit["points"][2], ipostit["points"][3], c[index][0]))\
                                    + src.model.processing.get_area((ipostit["points"][3], ipostit["points"][0], c[index][0]))
                        if pointarea < rectanglearea*1.1:
                                contained = True
                        if pointarea < rectanglearea*1.25 and not contained:
                            if not array:
                                array.append(idx)

                            elif idx is not array[-1]:
                                array.append(idx)

                    for idx, jpostit in enumerate(canvas.get_postits()):
                        if not jpostit.physical:
                            postitpoints = jpostit.get_corner_points()
                            rectanglearea = src.model.processing.get_area(postitpoints)
                            pointarea = src.model.processing.get_area((postitpoints[0], postitpoints[1], c[index][0])) \
                                    + src.model.processing.get_area((postitpoints[1], postitpoints[2], c[index][0]))\
                                    + src.model.processing.get_area((postitpoints[2], postitpoints[3], c[index][0]))\
                                    + src.model.processing.get_area((postitpoints[3], postitpoints[0], c[index][0]))
                            if pointarea < rectanglearea*1.1:
                                contained = True
                            if pointarea < rectanglearea*1.25 and not contained:
                                if not array:
                                    array.append(jpostit.get_id())
                                    line_start_point = c[index][0]
                                elif jpostit.get_id() is not array[-1]:
                                    array.append(jpostit.get_id())
                                    line_end_point = c[index][0]

                if len(array) > 1:
                    for i in range(0, len(array) - 1):
                        postit_idx = [-1, -1]
                        postit_id_start = 0
                        postit_id_end = 0
                        if len(str(array[i])) == 36:
                            postit_id_start = array[i]
                        else:
                            postit_idx[0] = array[i]
                        if len(str(array[i + 1])) == 36:
                            postit_id_end = array[i + 1]
                        else:
                            postit_idx[1] = array[i + 1]
                        if postit_id_start and postit_id_end:
                            found_connection = {
                                "postitIdStart": postit_id_start,
                                "postitIdEnd": postit_id_end
                            }
                            found_connections.append(found_connection)
                        elif postit_id_start and postit_idx[1] > -1:
                            found_connection = {
                                "postitIdStart": postit_id_start,
                                "postitIdx": postit_idx
                            }
                            found_connections.append(found_connection)
                        elif postit_id_end and postit_idx[0] > -1:
                            found_connection = {
                                "postitIdEnd": postit_id_end,
                                "postitIdx": postit_idx
                            }
                            found_connections.append(found_connection)
                        elif postit_idx[0] > -1 and postit_idx[1] > -1:
                            found_line = {
                                "postitIdx": postit_idx
                            }
                            found_connections.append(found_connection)
        return found_connections



