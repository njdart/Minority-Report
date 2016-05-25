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
                 id=None,
                 timestamp=datetime.datetime.now().isoformat(),
                 database=None):
        super(Image, self).__init__(id=id,
                         database=database)
        self.image = npArray
        self.timestamp = timestamp
        self.instanceConfigurationId = instanceConfigurationId

    @staticmethod
    def from_uri(instanceConfigurationId, uri='http://localhost:8080'):
        print('Getting image for config id {} from {}'.format(instanceConfigurationId, uri))

        try:
            response = requests.get(uri)
        except requests.exceptions.RequestException:
            print("Getting URI {} failed".format(uri))
            return None

        if response.status_code == 200:
            nparray = numpy.asarray(bytearray(response.content), dtype="uint8")
            return Image(instanceConfigurationId=instanceConfigurationId,
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
                     next_canvas_id,
                     current_canvas=None,
                     save=True,
                     min_postit_area=5000,
                     max_postit_area=40000,
                     len_tolerence=0.2,
                     min_colour_thresh=64,
                     max_colour_thresh=200,
                     save_postits=True):
        """
        :param next_canvas_id:
        :param current_canvas:
        :param save:
        :param min_postit_area:
        :param max_postit_area:
        :param len_tolerence:
        :param min_colour_thresh:
        :param max_colour_thresh:
        :param save_postits:
        :return: found_postits:

        Find postits in new image first
        Compare with postits in previous canvas, those that are not in new image are included as
        """
        from src.model.InstanceConfiguration import InstanceConfiguration
        from src.model.Postit import Postit
        userId = InstanceConfiguration.get(self.instanceConfigurationId).userId
        found_postits = []
        canvas_image = self.get_image_projection()
        display_ratio = (1920/canvas_image.shape[0])

        # Finding postits is based on saturation levels, first the image must be converted to HSV format
        hsv_image = cv2.cvtColor(canvas_image.copy(), cv2.COLOR_BGR2HSV)
        satthresh = 85  # CONST
        # All pixels with a saturation below threshold are set to black
        hsv_image[numpy.where((hsv_image < [255, satthresh, 255]).all(axis=2))] = [0, 0, 0]
        hsv_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        # All pixels below brightness threshold set to black
        # to remove any lines that have some saturation from reflections
        hsv_image[numpy.where((hsv_image < [100, 100, 100]).all(axis=2))] = [0, 0, 0]
        # cv2.imshow("debug", cv2.resize(hsv_image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
        # cv2.waitKey(0)
        # Convert image to grayscale and then canny filter and get contour
        gray_img = cv2.cvtColor(hsv_image, cv2.COLOR_BGR2GRAY)
        edge_gray = cv2.Canny(gray_img, 1, 30)
        # cv2.imshow("debug", cv2.resize(edge_gray, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
        # cv2.waitKey(0)
        (_, contours, _) = cv2.findContours(edge_gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        postitPts = []
        postitImages = []
        postitPos = []

        for c in contours:
            box = cv2.boxPoints(cv2.minAreaRect(c))
            box = numpy.int0(box)
            # print(cv2.contourArea(box))
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
                    postitPts.append(src.model.processing.order_points(numpy.array(postit_pts)))
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
                postit = Postit(physicalFor=userId,
                                canvas = next_canvas_id,
                                topLeftX=postitPts[idx][0][0],
                                topLeftY=postitPts[idx][0][1],
                                topRightX=postitPts[idx][1][0],
                                topRightY=postitPts[idx][1][1],
                                bottomRightX=postitPts[idx][2][0],
                                bottomRightY=postitPts[idx][2][1],
                                bottomLeftX=postitPts[idx][3][0],
                                bottomLeftY=postitPts[idx][3][1],
                                displayPosX=postitPts[idx][0][0]*display_ratio,
                                displayPosY=postitPts[idx][0][1]*display_ratio,
                                colour=guessed_colour,
                                image=self.get_id())

                if save_postits:
                    postit.create(self.database)

                found_postits.append(postit)

        if current_canvas is not None:
            old_postits = current_canvas.get_postits()
            missing_postits = []
            for o, old_postit in enumerate(old_postits):
                odes = old_postit.get_descriptors()
                good = numpy.zeros(len(found_postits), dtype=numpy.int)
                maxidx = -1
                IDs = []
                for n, new_postit in enumerate(found_postits):
                    ndes = new_postit.get_descriptors()
                    # Create BFMatcher object
                    bf = cv2.BFMatcher()
                    if len(ndes) > 0 and len(odes) > 0:
                        # Match descriptors
                        matches = bf.knnMatch(ndes, odes, k=2)
                        IDs.append(old_postit.get_id())
                        for a, b in matches:
                            if a.distance < (0.75*b.distance):
                                good[n] += 1
                    else:
                        print("oops")
                        cv2.imshow("debug", odes)
                        cv2.waitKey(0)

                print(good)
                if max(good) > 20:
                    pass
                else:
                    missing_postits.append(old_postit)
            for missing_postit in missing_postits:
                postit = Postit(physicalFor=None,
                                canvas = next_canvas_id,
                                topLeftX=missing_postit.topLeftX,
                                topLeftY=missing_postit.topLeftY,
                                topRightX=missing_postit.topRightX,
                                topRightY=missing_postit.topRightY,
                                bottomRightX=missing_postit.bottomRightX,
                                bottomRightY=missing_postit.bottomRightY,
                                bottomLeftX=missing_postit.bottomLeftX,
                                bottomLeftY=missing_postit.bottomLeftY,
                                displayPosX=missing_postit.displayPosX,
                                displayPosY=missing_postit.displayPosY,
                                colour=missing_postit.colour,
                                image=missing_postit.image.get_id())
                if save_postits:
                    postit.create(self.database)
                found_postits.append(postit)
        return found_postits

    def find_connections(self, postits, next_canvas_id, save=True):
        from src.model.InstanceConfiguration import InstanceConfiguration
        from src.model.Connection import Connection

        found_connections = []
        canvas_image = self.get_image_projection()
        edged = src.model.processing.edge(canvas_image)
        (_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for c in cnts:
            debug_img = canvas_image.copy()
            if cv2.arcLength(c, True) > 300:
                connectionList = []


                for index in range(0, len(c), 10):
                    contained = False
                    for idx, ipostit in enumerate(postits):
                        ipostitpoints = ipostit.get_corner_points()
                        rectanglearea = src.model.processing.get_area(ipostitpoints)
                        pointarea = src.model.processing.get_area((ipostitpoints[0], ipostitpoints[1], c[index][0]))\
                                    + src.model.processing.get_area((ipostitpoints[1], ipostitpoints[2], c[index][0]))\
                                    + src.model.processing.get_area((ipostitpoints[2], ipostitpoints[3], c[index][0]))\
                                    + src.model.processing.get_area((ipostitpoints[3], ipostitpoints[0], c[index][0]))
                        if pointarea < rectanglearea*1.1:
                                contained = True
                        if pointarea < rectanglearea*1.25 and not contained:
                            if not connectionList:
                                connectionList.append(ipostit.get_id())

                            elif ipostit.get_id() is not connectionList[-1]:
                                connectionList.append(ipostit.get_id())

                if len(connectionList) > 1:
                    for i in range(0, len(connectionList) - 1):
                        postit_id_start = 0
                        postit_id_end = 0
                        if len(str(connectionList[i])) == 36:
                            postit_id_start = connectionList[i]
                        if len(str(connectionList[i + 1])) == 36:
                            postit_id_end = connectionList[i + 1]
                        if postit_id_start and postit_id_end:
                            found_connection = {
                                "postitIdStart": postit_id_start,
                                "postitIdEnd": postit_id_end
                            }
                            found_connections.append(found_connection)
        if(found_connections):
            connection = Connection(start=found_connections[0]["postitIdStart"],
                                    finish=found_connections[0]["postitIdEnd"],
                                    canvas=next_canvas_id)
            if save:
                connection.create(self.database)
        return found_connections

    def update_canvases(self, new_postits, connections, current_canvas, next_canvas_id):
        from src.model.Canvas import Canvas
        from src.model.Postit import Postit



        new_canvas = Canvas(session=self.get_instance_configuration().sessionId,
                            id=next_canvas_id,
                            postits=new_postits,
                            connections=connections,
                            derivedFrom=current_canvas.id if current_canvas is not None else None,
                            derivedAt=datetime.datetime.now())
        new_canvas.create(self.database)

        return [new_canvas]
