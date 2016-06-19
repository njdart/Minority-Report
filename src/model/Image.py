import os
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

        # print(instanceConfiguration.get_projection_corner_points())

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

    def find_stickyNotes(self,
                     next_canvas_id,
                     current_canvas=None,
                     save=True,
                     min_stickyNote_area=6000,
                     max_stickyNote_area=40000,
                     len_tolerence=0.15,
                     min_colour_thresh=64,
                     max_colour_thresh=220,
                     save_stickyNotes=True):
        """
        :param next_canvas_id:
        :param current_canvas:
        :param save:
        :param min_stickyNote_area:
        :param max_stickyNote_area:
        :param len_tolerence:
        :param min_colour_thresh:
        :param max_colour_thresh:
        :param save_stickyNotes:
        :return: found_stickyNotes:

        Find stickyNotes in new image first
        Compare with stickyNotes in previous canvas, those that are not in new image are included as
        """
        from src.model.InstanceConfiguration import InstanceConfiguration
        from src.model.StickyNote import StickyNote

        userId = InstanceConfiguration.get(self.instanceConfigurationId).userId
        old_to_new_stickyNotes = [] # List of old id and corresponding new id
        found_stickyNotes = []
        canvas_image = self.get_image_projection()
        display_ratio = (1920.0/canvas_image.shape[1])
        # Finding stickyNotes is based on saturation levels, first the image must be converted to HSV format
        hsv_image = cv2.cvtColor(canvas_image.copy(), cv2.COLOR_BGR2HSV)
        satthresh = 100  # CONST
        # All pixels with a saturation below threshold are set to black
        hsv_image[numpy.where((hsv_image < [255, satthresh, 255]).all(axis=2))] = [0, 0, 0]
        hsv_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        # All pixels below brightness threshold set to black
        # to remove any lines that have some saturation from reflections
        hsv_image[numpy.where((hsv_image < [90, 120, 160]).all(axis=2))] = [0, 0, 0]
        # cv2.imwrite("debug/stickyNote-"+str(next_canvas_id)+".png", hsv_image)
        # Convert image to grayscale and then canny filter and get contour
        gray_img = cv2.cvtColor(hsv_image, cv2.COLOR_BGR2GRAY)
        gray_img = cv2.dilate(gray_img, numpy.ones((7, 7)))
        edge_gray = cv2.Canny(gray_img, 150, 200)
        # cv2.imwrite("debug/stickyNoteEdge-"+str(next_canvas_id)+".png", edge_gray)
        (_, contours, _) = cv2.findContours(edge_gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        stickyNotePts = []
        stickyNoteImages = []
        stickyNotePos = []

        for c in contours:
            box = cv2.boxPoints(cv2.minAreaRect(c))
            box = numpy.int0(box)
            # Check the area of the stickyNotes to see if they fit within the expected range
            if (cv2.contourArea(box) > min_stickyNote_area) and (cv2.contourArea(box) < max_stickyNote_area):
                # print(cv2.contourArea(box))
                length = numpy.math.hypot(box[0, 0] - box[1, 0], box[0, 1] - box[1, 1])
                height = numpy.math.hypot(box[2, 0] - box[1, 0], box[2, 1] - box[1, 1])
                # Check to see how similar the lengths are as a measure of squareness
                if length * (2 - len_tolerence) < length + height < length * (2 + len_tolerence):
                    # print("len : "+str(length))
                    rectangle = cv2.boundingRect(c)
                    flat_contour = c.flatten()
                    # Create arrays for finding the corners of the stickyNotes
                    canvx = numpy.zeros([int(len(flat_contour) / 2), 1])
                    canvy = numpy.zeros([int(len(flat_contour) / 2), 1])
                    topLeft = numpy.zeros(int(len(flat_contour) / 2))
                    topRight = numpy.zeros(int(len(flat_contour) / 2))
                    bottomRight = numpy.zeros(int(len(flat_contour) / 2))
                    bottomLeft = numpy.zeros(int(len(flat_contour) / 2))
                    # To calculate the four corners each point is scored on how well it fits a corner.
                    # The range of X and Y values is scaled to a 0 to 1 scale.
                    # The points x and y score are then added together giving a score between 0 and 2.
                    # The point that has the highest score for a corner is most likely to be that corner.
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
                        topLeft[idx] = (1 - lx) + (1 - ly)
                        topRight[idx] = lx + (1 - ly)
                        bottomRight[idx] = lx + ly
                        bottomLeft[idx] = (1 - lx) + ly

                    maxTopLeft = numpy.argmax(topLeft)
                    maxTopRight = numpy.argmax(topRight)
                    maxBottomRight = numpy.argmax(bottomRight)
                    maxBottomLeft = numpy.argmax(bottomLeft)
                    stickyNote_pts = [(canvx[maxTopLeft][0], canvy[maxTopLeft][0]),
                                  (canvx[maxTopRight][0], canvy[maxTopRight][0]),
                                  (canvx[maxBottomRight][0], canvy[maxBottomRight][0]),
                                  (canvx[maxBottomLeft][0], canvy[maxBottomLeft][0])]
                    # Crop and transform image based on points
                    stickyNoteimg = src.model.processing.four_point_transform(canvas_image, numpy.array(stickyNote_pts))
                    stickyNotePts.append(src.model.processing.order_points(numpy.array(stickyNote_pts)))
                    stickyNoteImages.append(stickyNoteimg)
                    stickyNotePos.append(rectangle)
        for idx, stickyNote_image in enumerate(stickyNoteImages):
            # Calculate average stickyNote colour in order to guess the colour of the stickyNote
            gray_image = cv2.cvtColor(stickyNote_image, cv2.COLOR_BGR2GRAY)
            red_total = green_total = blue_total = 0
            (width, height, depth) = stickyNote_image.shape
            for y in range(height):
                for x in range(width):
                    if min_colour_thresh < gray_image[x, y] < max_colour_thresh:
                        b, g, r = stickyNote_image[x, y]
                        red_total += r
                        green_total += g
                        blue_total += b

            count = width * height

            red_average = red_total / count
            green_average = green_total / count
            blue_average = blue_total / count

            guessed_colour = src.model.processing.guess_colour(red_average, green_average, blue_average)
            # Only if a stickyNote colour valid create a stickyNote
            if guessed_colour is not None:
                stickyNote = StickyNote(physicalFor=userId,
                                canvas = next_canvas_id,
                                topLeftX=stickyNotePts[idx][0][0],
                                topLeftY=stickyNotePts[idx][0][1],
                                topRightX=stickyNotePts[idx][1][0],
                                topRightY=stickyNotePts[idx][1][1],
                                bottomRightX=stickyNotePts[idx][2][0],
                                bottomRightY=stickyNotePts[idx][2][1],
                                bottomLeftX=stickyNotePts[idx][3][0],
                                bottomLeftY=stickyNotePts[idx][3][1],
                                displayPosX=(stickyNotePts[idx][0][0]+stickyNotePts[idx][2][0])*display_ratio*0.5,
                                displayPosY=(stickyNotePts[idx][0][1]+stickyNotePts[idx][2][1])*display_ratio*0.5,
                                colour=guessed_colour,
                                image=self.get_id())
                if save_stickyNotes:
                    stickyNote.create(self.database)
                found_stickyNotes.append(stickyNote)

        if current_canvas is not None:
            old_stickyNotes = current_canvas.get_stickyNotes()
            missing_stickyNotes = []
            old_stickyNote_info =[]
            new_stickyNote_info = []
            for old_stickyNote in old_stickyNotes:
                old_info = (old_stickyNote.id, old_stickyNote.get_descriptors())
                old_stickyNote_info.append(old_info)

            for new_stickyNote in found_stickyNotes:
                new_info = (new_stickyNote.id, new_stickyNote.get_descriptors())
                new_stickyNote_info.append(new_info)


            for old_index, old_stickyNote in enumerate(old_stickyNotes):
                good = numpy.zeros(len(found_stickyNotes), dtype=numpy.int)
                IDs = []
                odes = old_stickyNote_info[old_index][1]
                for new_index, new_info in enumerate(new_stickyNote_info):
                    ndes = new_info[1]
                    # Create BFMatcher object
                    bf = cv2.BFMatcher()
                    if ndes is not None and odes is not None:
                        if len(ndes) > 0 and len(odes) > 0:
                            matches = bf.knnMatch(ndes, odes, k=2)
                            IDs.append(old_stickyNote.get_id())
                            for a, b in matches:
                                if a.distance < (0.75*b.distance):
                                    good[new_index] += 1
                        else:
                            cv2.imshow("debug", odes)
                            cv2.waitKey(0)
                print(good)
                if odes is not None:
                    if not len(good) == 0:
                        if max(good) > 12: #len(odes)*0.1:
                            match_idx = numpy.argmax(good)
                            old_to_new_stickyNote = (old_stickyNote_info[old_index][0], new_stickyNote_info[match_idx][0])
                            old_to_new_stickyNotes.append(old_to_new_stickyNote)
                        else:
                            missing_stickyNotes.append(old_stickyNote)
                    else:
                            missing_stickyNotes.append(old_stickyNote)
            for missing_stickyNote in missing_stickyNotes:
                if missing_stickyNote.physicalFor == userId:
                    stickyNote = StickyNote(physicalFor=None,
                                    canvas=next_canvas_id,
                                    topLeftX=missing_stickyNote.topLeftX,
                                    topLeftY=missing_stickyNote.topLeftY,
                                    topRightX=missing_stickyNote.topRightX,
                                    topRightY=missing_stickyNote.topRightY,
                                    bottomRightX=missing_stickyNote.bottomRightX,
                                    bottomRightY=missing_stickyNote.bottomRightY,
                                    bottomLeftX=missing_stickyNote.bottomLeftX,
                                    bottomLeftY=missing_stickyNote.bottomLeftY,
                                    displayPosX=missing_stickyNote.displayPosX,
                                    displayPosY=missing_stickyNote.displayPosY,
                                    colour=missing_stickyNote.colour,
                                    image=missing_stickyNote.image.get_id())
                else:
                    stickyNote = StickyNote(physicalFor=missing_stickyNote.physicalFor,
                                    canvas=next_canvas_id,
                                    topLeftX=missing_stickyNote.topLeftX,
                                    topLeftY=missing_stickyNote.topLeftY,
                                    topRightX=missing_stickyNote.topRightX,
                                    topRightY=missing_stickyNote.topRightY,
                                    bottomRightX=missing_stickyNote.bottomRightX,
                                    bottomRightY=missing_stickyNote.bottomRightY,
                                    bottomLeftX=missing_stickyNote.bottomLeftX,
                                    bottomLeftY=missing_stickyNote.bottomLeftY,
                                    displayPosX=missing_stickyNote.displayPosX,
                                    displayPosY=missing_stickyNote.displayPosY,
                                    colour=missing_stickyNote.colour,
                                    image=missing_stickyNote.image.get_id())

                old_to_new_stickyNote = (missing_stickyNote.id, stickyNote.id)
                old_to_new_stickyNotes.append(old_to_new_stickyNote)
                if save_stickyNotes:
                    stickyNote.create(self.database)
                found_stickyNotes.append(stickyNote)
        stickyNote_delete_list = []
        for pidx, new_stickyNote in enumerate(found_stickyNotes):
            if new_stickyNote.displayPosX < 200 and new_stickyNote.displayPosY <200:
                # print(str(new_stickyNote.displayPosX)+", "+str(new_stickyNote.displayPosY))

                stickyNote_delete_list.append((new_stickyNote.id, new_stickyNote))
                # print("deleting stickyNote:", new_stickyNote.id, new_stickyNote.displayPosX, new_stickyNote.displayPosY)
        for del_post in stickyNote_delete_list:
            rmv_from_old_to_new = [i for i, pair in enumerate(old_to_new_stickyNotes) if pair[1] == del_post[0]]
            for index in reversed(rmv_from_old_to_new):
                del old_to_new_stickyNotes[index]
            found_stickyNotes.remove(del_post[1])
            StickyNote.get(id=del_post[0]).delete()
        return (found_stickyNotes, old_to_new_stickyNotes)

    def find_connections(self, stickyNotes, old_to_new_stickyNotes, next_canvas_id, current_canvas, save=True):
        from src.model.Connection import Connection

        found_connections = []
        canvas_image = self.get_image_projection()
        edged = src.model.processing.edge(canvas_image)
        # cv2.imwrite("debug/lines-"+str(next_canvas_id)+".png",
        #             cv2.resize(edged, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
        (_, line_contours, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        line_ratio = (1920.0/canvas_image.shape[1])
        postit_ratio=[]
        for idx, istickyNote in enumerate(stickyNotes):
            postit_canvas_image = istickyNote.get_image()
            postit_ratio.append(1920.0/postit_canvas_image.get_image_projection().shape[1])
        for line_contour in line_contours:
            debug_img = canvas_image.copy()
            if cv2.arcLength(line_contour, True) > 100:
                connectionList = []

                for index in range(0, len(line_contour), 10):
                    contained = False
                    #debugImage = cv2.circle(canvas_image.copy(), (line_contour[index][0][0],line_contour[index][0][1]),4,[0,0,255],thickness=5)
                    #cv2.imwrite(str(index) + "debug.png", cv2.resize(debugImage,None,fx=0.25, fy=0.25,))

                    for idx, istickyNote in enumerate(stickyNotes):
                        istickyNotepoints = istickyNote.get_corner_points()
                        rectanglearea = src.model.processing.get_area(istickyNotepoints)
                        scaled_contour_point = (line_contour[index][0][0]*line_ratio, line_contour[index][0][1]*line_ratio)
                        if not istickyNote.physicalFor in ["None", None]:
                            pointarea = src.model.processing.get_area((((istickyNotepoints[0][0]+7)*postit_ratio[idx], (istickyNotepoints[0][1]+7)*postit_ratio[idx]),
                                                                       ((istickyNotepoints[1][0]-7)*postit_ratio[idx], (istickyNotepoints[1][1]+7)*postit_ratio[idx]),
                                                                       scaled_contour_point))\
                                        + src.model.processing.get_area((((istickyNotepoints[1][0]-7)*postit_ratio[idx], (istickyNotepoints[1][1]+7)*postit_ratio[idx]),
                                                                         ((istickyNotepoints[2][0]-7)*postit_ratio[idx], (istickyNotepoints[2][1]-7)*postit_ratio[idx]),
                                                                         scaled_contour_point))\
                                        + src.model.processing.get_area((((istickyNotepoints[2][0]-7)*postit_ratio[idx], (istickyNotepoints[2][1]-7)*postit_ratio[idx]),
                                                                         ((istickyNotepoints[3][0]+7)*postit_ratio[idx], (istickyNotepoints[3][1]-7)*postit_ratio[idx]),
                                                                         scaled_contour_point))\
                                        + src.model.processing.get_area((((istickyNotepoints[3][0]+7)*postit_ratio[idx], (istickyNotepoints[3][1]-7)*postit_ratio[idx]),
                                                                         ((istickyNotepoints[0][0]+7)*postit_ratio[idx], (istickyNotepoints[0][1]+7)*postit_ratio[idx]),
                                                                         scaled_contour_point))
                        else:
                            # print("physicalFor: {}".format(istickyNote.physicalFor))
                            stickyNotesize = istickyNote.get_image_keystoned().shape
                            noteX = istickyNote.displayPosX
                            noteY = istickyNote.displayPosY
                            pointarea = src.model.processing.get_area(((noteX - stickyNotesize[0]/2, noteY - stickyNotesize[1]/2),
                                                                       (noteX + stickyNotesize[0]/2, noteY - stickyNotesize[1]/2),
                                                                       scaled_contour_point))\
                                        + src.model.processing.get_area(((noteX + stickyNotesize[0]/2, noteY - stickyNotesize[1]/2),
                                                                         (noteX + stickyNotesize[0]/2, noteY + stickyNotesize[1]/2),
                                                                         scaled_contour_point)) \
                                        + src.model.processing.get_area(((noteX + stickyNotesize[0]/2, noteY+stickyNotesize[1]/2),
                                                                         (noteX - stickyNotesize[0]/2, noteY+stickyNotesize[1]/2),
                                                                         scaled_contour_point)) \
                                        + src.model.processing.get_area(((noteX - stickyNotesize[0]/2, noteY+stickyNotesize[1]/2),
                                                                         (noteX - stickyNotesize[0]/2, noteY-stickyNotesize[1]/2),
                                                                         scaled_contour_point))
                           
                        if pointarea < rectanglearea*1.05:
                            contained = True

                        if pointarea < rectanglearea*1.1 and not contained:
                            if not connectionList:
                                connectionList.append(istickyNote.get_id())
                                #debugImage = cv2.circle(canvas_image.copy(), (line_contour[index][0][0],line_contour[index][0][1]),4,[0,255,0],thickness=5)
                                #cv2.imshow("debug", cv2.resize(debugImage,None,fx=0.25, fy=0.25,))
                                #cv2.waitKey(0)

                            elif istickyNote.get_id() is not connectionList[-1]:
                                connectionList.append(istickyNote.get_id())
                                #debugImage = cv2.circle(canvas_image.copy(), (line_contour[index][0][0],line_contour[index][0][1]),4,[0,255,0],thickness=5)
                                #cv2.imshow("debug", cv2.resize(debugImage,None,fx=0.25, fy=0.25,))
                                #cv2.waitKey(0)

                if len(connectionList) > 1:
                    print(connectionList)
                    for connection_index in range(0, len(connectionList) - 1):
                        stickyNote_id_start = 0
                        stickyNote_id_end = 0
                        if len(str(connectionList[connection_index])) == 36:
                            stickyNote_id_start = connectionList[connection_index]
                        if len(str(connectionList[connection_index + 1])) == 36:
                            stickyNote_id_end = connectionList[connection_index + 1]
                        if stickyNote_id_start and stickyNote_id_end:
                            found_connection = {
                                "stickyNoteIdStart": stickyNote_id_start,
                                "stickyNoteIdEnd": stickyNote_id_end
                            }
                            found_connections.append(found_connection)
        new_connections = []
        if current_canvas:
            old_connections = Connection.get_by_property(prop="canvas", value=current_canvas.id)
            for old_connection in old_connections:
                new_start_id = 0
                new_finish_id = 0
                for id_pair in old_to_new_stickyNotes:
                    if old_connection.start == id_pair[0]:
                        new_start_id = id_pair[1]
                    if old_connection.finish == id_pair[0]:
                        new_finish_id = id_pair[1]
                if new_start_id and new_finish_id:
                    connection = Connection(start=new_start_id,
                                                    finish=new_finish_id,
                                                    canvas=next_canvas_id)
                    if save:
                        connection.create(self.database)
                    new_connections.append(connection)

        if found_connections:
            for next_connection in found_connections:
                unique = True
                if new_connections:
                    for new_connection in new_connections:
                        if (str(next_connection["stickyNoteIdStart"]) == str(new_connection.start)
                            and str(next_connection["stickyNoteIdEnd"]) == str(new_connection.finish)
                            or (str(next_connection["stickyNoteIdEnd"]) == str(new_connection.start)
                                and str(next_connection["stickyNoteIdStart"]) == str(new_connection.finish))):
                            unique = False

                if unique:
                    connection = Connection(start=next_connection["stickyNoteIdStart"],
                                                finish=next_connection["stickyNoteIdEnd"],
                                                canvas=next_canvas_id)
                    if save:
                        connection.create(self.database)
                    new_connections.append(connection)


        return new_connections

    def update_canvases(self, new_stickyNotes, connections, current_canvas, next_canvas_id):
        from src.model.Canvas import Canvas

        new_canvas = Canvas(session=self.get_instance_configuration().sessionId,
                            id=next_canvas_id,
                            stickyNotes=new_stickyNotes,
                            connections=connections,
                            derivedFrom=current_canvas.id if current_canvas is not None else None,
                            derivedAt=datetime.datetime.now())
        new_canvas.create(self.database)

        return [new_canvas]
