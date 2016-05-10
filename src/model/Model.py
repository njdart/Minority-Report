import cv2
import numpy as np
import uuid
import json
import datetime
from src.model.GraphExtractor import GraphExtractor
from src.model.Canvas import Canvas
from src.model.Postit import Postit
import zipfile
import os
import requests


class Model:
    """
    Model of the board storing history of the canvas and settings used to ge extract that information
    """

    def __init__(self):
        self.canvasList = []
        self.canvasConnections = []
        self.prevCanvasID = None
        self.snapshot_time = 0
        self.new_id = None

        self.calibImage = []

        self.simpleBounds = []
        self.canvasBounds = []
        self.raw_image = []
        self.activePostits = []

        self.postitConnections = []

        self.minPostitArea = 2000
        self.maxPostitArea = 10000
        self.lenTolerence = 0.4
        self.minColourThresh = 64

        self.maxColourThresh = 200
        self.postitThresh = 120
        self.sigma = 0.33

        self.debug = False

    # ========================================================= #
    # Return current rawImage
    def get_raw_image(self):
        return self.raw_image

    # Return current canvasBounds
    def get_canvas_bounds(self):
        return self.canvasBounds

    # Change canvas bounds for when the auto-generated bounds are wrong
    def set_canvas_bounds(self, new_bounds):
        self.canvasBounds = new_bounds

    # From the current calibImage calculates likely boundaries of the canvas
    def run_auto_calibrate(self, show_debug=False):
        self.canvasBounds = self.find_canvas(self.calibImage, show_debug)

    # Returns position of postits and relationships of current graph
    def get_abstract_graph(self):
        positions = []
        ids = []
        for postit in self.activePostits:
            positions.append(postit.location)
            ids.append(postit.ID)

        postit = {
            "position": positions,
            "ID": ids
        }
        graph = {
            "connections": self.postitConnections,
            "postit": postit
        }
        return graph

    # Return canvas from history using the UUID associated with it
    def get_canvas(self, canv_id):
        for canvas in self.canvasList:
            if canvas.get_id() == canv_id:
                return canvas
        return None

    # Create .zip archive of the canvas history
    def save(self, filename):
        data = []
        zf = zipfile.ZipFile(filename + '.zip', mode='w')
        for canv in self.canvasList:
            cv2.imwrite(str(canv.ID) + ".png", canv.rawImage)
            postits = []
            connections = []
            for canv_postit in canv.postits:
                postit = {
                    "colour": canv_postit.colour,
                    "uuid": str(canv_postit.ID),
                    "x": canv_postit.location[0],
                    "y": canv_postit.location[1],
                    "height": canv_postit.size[1],
                    "width": canv_postit.size[0],
                    "isPhysical": canv_postit.physical,
                    "lastCanvasID": str(canv_postit.last_canvas_ID)
                }
                postits.append(postit)
            for cxn in canv.connections:
                connection = {
                    "from": str(cxn[0]),
                    "to": str(cxn[1]),
                    "type": "line"
                }
                connections.append(connection)
            canvas = {
                "uuid": str(canv.ID),
                "derivedAt": str(canv.timestamp),
                "derivedFrom": str(canv.derivedFrom),
                "canvas": {
                    "top-left": {
                        "x": canv.bounds[0],
                        "y": canv.bounds[1]
                    },
                    "top-right": {
                        "x": canv.bounds[0] + canv.bounds[2],
                        "y": canv.bounds[1]
                    },
                    "bottom-left": {
                        "x": canv.bounds[0],
                        "y": canv.bounds[1] + canv.bounds[3]
                    },
                    "bottom-right": {
                        "x": canv.bounds[0] + canv.bounds[2],
                        "y": canv.bounds[1] + canv.bounds[3]
                    }
                },
                "width": canv.rawImage.shape[1],
                "height": canv.rawImage.shape[0],
                "postits": postits,
                "connections": connections
            }

            zf.write(str(canv.ID) + ".png")
            os.remove(str(canv.ID) + ".png")
            data.append(canvas)
        with open("canvas_history.json", 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=2, separators=(',', ':'))
        zf.write("canvas_history.json")
        os.remove("canvas_history.json")
        zf.close()

    # From .zip archive reconstruct the cavas history
    def load(self, filename):
        zf = zipfile.ZipFile(filename + '.zip')
        data_file = zf.read("canvas_history.json").decode("utf-8")
        data = json.loads(data_file)
        for dataCanvas in data:
            image = zf.read(dataCanvas["uuid"] + ".png")
            data_board_image = cv2.imdecode(np.frombuffer(image, np.uint8), 1)
            data_bounds = [dataCanvas["canvas"]["top-left"]["x"], dataCanvas["canvas"]["top-left"]["y"],
                           dataCanvas["canvas"]["bottom-right"]["x"] - dataCanvas["canvas"]["top-left"]["x"],
                           dataCanvas["canvas"]["bottom-right"]["y"] - dataCanvas["canvas"]["top-left"]["y"]]
            data_postits = []
            for dataPostit in dataCanvas["postits"]:
                postit = Postit(dataPostit["uuid"],
                                dataPostit["x"],
                                dataPostit["y"],
                                dataPostit["width"],
                                dataPostit["height"],
                                dataPostit["colour"],
                                dataPostit["isPhysical"],
                                dataPostit["lastCanvasID"])
                data_postits.append(postit)
            dataConnections = []
            for dataLine in dataCanvas["connections"]:
                cxn = [dataLine["from"], dataLine["to"]]
                dataConnections.append(cxn)

            canvas = Canvas(dataCanvas["uuid"],
                            dataCanvas["derivedAt"],
                            data_board_image,
                            data_bounds,
                            data_postits,
                            dataConnections,
                            dataCanvas["derivedFrom"])
            self.canvasList.append(canvas)
        return None

    # ======================================================== #

    # Set a new calibImage
    def new_calib_image(self, image):
        self.calibImage = image

    # Set a new rawImage triggering a new canvas to be taken
    def new_raw_image(self, image, time, update=0):
        self.raw_image = image
        self.snapshot_time = time
        if update:
            self.update()

    # From calibImage find likely canvasBounds
    def find_canvas(self, image, show_debug):
        smooth_img = self.bw_smooth(image)
       # blur = cv2.GaussianBlur(smooth_img,(5,5),0)
        ret3,gray_board = cv2.threshold(smooth_img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        #(__, gray_board) = cv2.threshold(smooth_img, 200, 255, cv2.THRESH_OTSU)

        (__, board_contours, __) = cv2.findContours(gray_board, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(c) for c in board_contours]

        max_index = np.argmax(areas)
        canvas_contour = board_contours[max_index]
        self.simpleBounds = cv2.boundingRect(canvas_contour)
        fcanvas_contours = canvas_contour.flatten()
        canvx = np.zeros([int(len(fcanvas_contours) / 2), 1])
        canvy = np.zeros([int(len(fcanvas_contours) / 2), 1])
        l1 = np.zeros(int(len(fcanvas_contours) / 2))
        l2 = np.zeros(int(len(fcanvas_contours) / 2))
        l3 = np.zeros(int(len(fcanvas_contours) / 2))
        l4 = np.zeros(int(len(fcanvas_contours) / 2))
        for i in range(0, len(fcanvas_contours), 2):
            canvx[int(i / 2)] = fcanvas_contours[i]
            canvy[int(i / 2)] = fcanvas_contours[i + 1]
        xmax = np.max(canvx)
        ymax = np.max(canvy)
        xmin = np.min(canvx)
        ymin = np.min(canvy)
        for n in range(0, len(canvx)):
            lx = ((canvx[n] - xmin) / (xmax - xmin))
            ly = ((canvy[n] - ymin) / (ymax - ymin))
            l1[n] = (1 - lx) + (1 - ly)
            l2[n] = lx + (1 - ly)
            l3[n] = lx + ly
            l4[n] = (1 - lx) + ly
        max1 = np.argmax(l1)
        max2 = np.argmax(l2)
        max3 = np.argmax(l3)
        max4 = np.argmax(l4)
        canvas_pts = [(canvx[max1][0], canvy[max1][0]),
                      (canvx[max2][0], canvy[max2][0]),
                      (canvx[max3][0], canvy[max3][0]),
                      (canvx[max4][0], canvy[max4][0])]

        if show_debug:
            debug_image = image.copy()
            for c in board_contours:
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(debug_image, board_contours, max_index, (0, 0, 255), 2)
                cv2.circle(debug_image, (canvx[max1], canvy[max1]), 4, (0, 255, 0), thickness=5)
                cv2.circle(debug_image, (canvx[max2], canvy[max2]), 4, (0, 255, 0), thickness=5)
                cv2.circle(debug_image, (canvx[max3], canvy[max3]), 4, (0, 255, 0), thickness=5)
                cv2.circle(debug_image, (canvx[max4], canvy[max4]), 4, (0, 255, 0), thickness=5)
            cv2.imshow("debug", cv2.resize(debug_image, None, fx=0.25, fy=0.25))
            cv2.waitKey(0)

        return np.array(canvas_pts)

    # Takes 4 corner points and use them to try and unwarp a rectangular image
    def four_point_transform(self, image, pts):
        # obtain a consistent order of the points and unpack them
        # individually
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(width_a), int(width_b))

        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(height_a), int(height_b))

        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]], dtype="float32")

        # compute the perspective transform matrix and then apply it
        transform_matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, transform_matrix, (max_width, max_height))

        # return the warped image
        return warped

    # Orders 4 points starting top-left going clockwise
    def order_points(self, pts):
        # initialzie a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype="float32")

        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # return the ordered coordinates
        return rect

    # Using canvasBounds on rawImage extract an image of the canvas
    def get_canvas_image(self):
        return self.four_point_transform(image=self.raw_image, pts=self.canvasBounds)

    # Get the image of a previous canvas
    def get_prev_canvas_image(self, ID):
        if ID == self.new_id:
            return self.get_canvas_image()
        else:
            canvas = self.get_canvas(canv_id=ID)
            return self.four_point_transform(image=canvas.image, pts=self.canvasBounds)

    # Compare current graph with previous graph
    def compare_prev(self, newGraph):
        postit_ids = self.update_postits(new_postits=newGraph["postits"])
        self.update_lines(postit_ids=postit_ids, lines=newGraph["lines"])

    # Compare a new list of postits to the list of known active postits
    def update_postits(self, new_postits):
        postit_ids = []
        active_postits_found = []
        newUniquePostits = []
        for o, newPostit in enumerate(new_postits):
            maxidx = -1
            good = np.zeros(len(self.activePostits), dtype=np.int)

            IDs = []
            for p, oldPostit in enumerate(self.activePostits):
                oim = self.bw_smooth(image=oldPostit.get_postit_image(self.get_prev_canvas_image(oldPostit.get_canvas())))
                nim = self.bw_smooth(image=newPostit["image"])
                # Initiate SIFT detector
                sift = cv2.xfeatures2d.SIFT_create()

                # Find the keypoints and descriptors with SIFT
                kp1, des1 = sift.detectAndCompute(oim, None)
                kp2, des2 = sift.detectAndCompute(nim, None)

                # Create BFMatcher object
                bf = cv2.BFMatcher()
                if len(kp1) > 0 and len(kp2) > 0:
                    # Match descriptors
                    matches = bf.knnMatch(des2, des1, k=2)
                    IDs.append(oldPostit.get_id())
                    for m, n in matches:
                        if m.distance < (0.75 * n.distance):
                            good[p] += 1
                else:
                    cv2.imshow("thing", oim)
                    cv2.waitKey(0)

            # print(good)
            try:
                if max(good) > 10:
                    maxidx = np.argmax(good)
            except:
                pass

            # print(len(goodMatches))
            if maxidx == -1:
                # Create new entry on list of active postits and then add ID to list
                new_id = uuid.uuid4()
                created_postit = Postit(x=newPostit["position"][0],
                                        y=newPostit["position"][1],
                                        width=newPostit["position"][2],
                                        height=newPostit["position"][3],
                                        pnt1X=newPostit["points"][0][0],
                                        pnt1Y=newPostit["points"][0][1],
                                        pnt2X=newPostit["points"][1][0],
                                        pnt2Y=newPostit["points"][1][1],
                                        pnt3X=newPostit["points"][2][0],
                                        pnt3Y=newPostit["points"][2][1],
                                        pnt4X=newPostit["points"][3][0],
                                        pnt4Y=newPostit["points"][3][1],
                                        colour=newPostit["colour"],
                                        id=new_id,
                                        canvas=self.new_id
                                        )
                newUniquePostits.append(created_postit)
                postit_ids.append(new_id)
                active_postits_found.append(new_id)
            else:
                # Return ID of Matched postits
                updating_postit = self.activePostits.pop(maxidx)
                postit_ids.append(updating_postit.get_id())
                active_postits_found.append(updating_postit.get_id())
                updating_postit.update_postit(x=newPostit["position"][0],
                                              y=newPostit["position"][1],
                                              width=newPostit["position"][2],
                                              height=newPostit["position"][3],
                                              pnt1X=newPostit["points"][0][0],
                                              pnt1Y=newPostit["points"][0][1],
                                              pnt2X=newPostit["points"][1][0],
                                              pnt2Y=newPostit["points"][1][1],
                                              pnt3X=newPostit["points"][2][0],
                                              pnt3Y=newPostit["points"][2][1],
                                              pnt4X=newPostit["points"][3][0],
                                              pnt4Y=newPostit["points"][3][1],
                                              colour=newPostit["colour"],
                                              canvas=self.new_id,
                                              physical=True
                                              )
                self.activePostits.insert(maxidx, updating_postit)

        for p, oldPostit in enumerate(self.activePostits):
            if oldPostit.get_id() not in active_postits_found:
                oldPostit.set_physical(False)
        self.activePostits.extend(newUniquePostits)

        return postit_ids

    # Compare lines found with know list of connections
    def update_lines(self, postit_ids, lines):
        for cxn in lines:
            if "postitIdStart" in cxn.keys():
                start = cxn["postitIdStart"]
            else:
                start = postit_ids[cxn["postitIdx"][0]]
            if "postitIdEnd" in cxn.keys():
                end = cxn["postitIdEnd"]
            else:
                end = postit_ids[cxn["postitIdx"][1]]
            connection = [start, end]
            # print(connection)
            if connection not in self.postitConnections:
                self.postitConnections.append(connection)

    # Change settings used in graph extraction
    def image_settings(self, mipa, mapa, lento, sig, mico, maco, poth):
        self.minPostitArea = mipa
        self.maxPostitArea = mapa
        self.lenTolerence = lento
        self.maxColourThresh = maco
        self.minColourThresh = mico
        self.postitThresh = poth
        self.sigma = sig

    # set wether debug info should be displayed
    def set_debug(self, state):
        self.debug = state

    # Smooth an image and convert to black and white wile maintaining features
    def bw_smooth(self, image):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        norm_img = clahe.apply(gray_img)
        smooth_img = cv2.bilateralFilter(norm_img, 3, 75, 75)
        return smooth_img

    def delete_binned(self, x1=0, y1=0, x2=200, y2=200):
        del_postits = []
        for postit in self.activePostits:
            post_pos = postit.get_position()
            if x1 < post_pos[0] < x2 and y1 < post_pos[1] < y2:
                del_postits.append(postit)
        for del_postit in del_postits:
            delcxns = []
            for cxn in self.postitConnections:
                if cxn[0] == del_postit.get_id() or cxn[1] == del_postit.get_id():
                    delcxns.append(cxn)
            for delcxn in delcxns:
                self.postitConnections.remove(delcxn)
            self.activePostits.remove(del_postit)

    # Main update loop using the current settings to extract data from current rawImage
    def update(self):
        canvas_image = self.get_canvas_image()
        extractor = GraphExtractor(image=canvas_image, previous_postits=self.activePostits)
        graph = extractor.extract_graph(show_debug=self.debug,
                                        min_postit_area=self.minPostitArea,
                                        max_postit_area=self.maxPostitArea,
                                        len_tolerence=self.lenTolerence,
                                        min_colour_thresh=self.minColourThresh,
                                        max_colour_thresh=self.maxColourThresh)
        self.new_id = uuid.uuid4()
        self.compare_prev(newGraph=graph)
        self.delete_binned()
        new_canvas = Canvas(image=self.raw_image,
                            canvasBounds=self.canvasBounds,
                            id=self.new_id,
                            postits=self.activePostits,
                            connections=self.postitConnections,
                            derivedFrom=self.prevCanvasID,
                            derivedAt=self.snapshot_time
                            )
        self.canvasConnections.append([self.prevCanvasID, self.new_id])
        self.prevCanvasID = self.new_id
        self.canvasList.append(new_canvas)

    # For testing construct the current canvas into a visual display for projecting back on to physical postits
    def display(self, canvas=-1):
        if len(self.canvasList):
            last_canvas = self.canvasList[canvas]
            disp_image = np.zeros((self.simpleBounds[3], self.simpleBounds[2], 3), np.uint8)
            cv2.line(disp_image, (0, 0), (200, 200), [150, 150, 150], thickness=4)
            cv2.line(disp_image, (0, 200), (200, 0), [150, 150, 150], thickness=4)
            cv2.line(disp_image, (0, 0), (200, 0), [150, 150, 150], thickness=4)
            cv2.line(disp_image, (0, 0), (0, 200), [150, 150, 150], thickness=4)
            cv2.line(disp_image, (200, 200), (200, 0), [150, 150, 150], thickness=4)
            cv2.line(disp_image, (200, 200), (0, 200), [150, 150, 150], thickness=4)

            for line in last_canvas.connections:
                start_point = (int(last_canvas.get_postit(line[0]).get_position()[0] +
                                   (last_canvas.get_postit(line[0]).get_size()[0]) / 2),
                               int(last_canvas.get_postit(line[0]).get_position()[1] +
                                   (last_canvas.get_postit(line[0]).get_size()[1]) / 2))
                end_point = (int(last_canvas.get_postit(line[1]).get_position()[0] +
                                 (last_canvas.get_postit(line[1]).get_size()[0]) / 2),
                             int(last_canvas.get_postit(line[1]).get_position()[1] +
                                 (last_canvas.get_postit(line[1]).get_size()[1]) / 2))
                cv2.line(disp_image, start_point, end_point, [255, 0, 0], thickness=4)

            for postit in last_canvas.postits:
                for canvas in self.canvasList:
                    if canvas.get_id() == postit.get_canvas():
                        postitImage = postit.get_postit_image(
                            self.four_point_transform(image=canvas.image, pts=self.canvasBounds)
                        )
                x1 = postit.get_position()[0]
                y1 = postit.get_position()[1]
                x2 = postit.get_position()[0] + postit.get_size()[0]
                y2 = postit.get_position()[1] + postit.get_size()[1]
                if postit.physical == 1:
                    cv2.rectangle(disp_image, (x1, y1), (x2, y2), (0, 0, 0), thickness=cv2.FILLED)
                    cv2.rectangle(disp_image, (x1, y1), (x2, y2), (0, 255, 0), thickness=4)
                elif postit.physical == 0:
                    cv2.rectangle(disp_image,
                                  (x1, y1),
                                  (x1 + postitImage.shape[1], y1 + postitImage.shape[0]),
                                  (0, 0, 0),
                                  thickness=cv2.FILLED)

                    postitImageTest = postitImage.copy()

                    Z = postitImageTest.reshape((-1,3))
                    # convert to np.float32
                    Z = np.float32(Z)
                    # define criteria, number of clusters(K) and apply kmeans()
                    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
                    K = 2
                    ret,label,center = cv2.kmeans(data=Z, K=K, bestLabels=None, criteria=criteria, attempts=10, flags=cv2.KMEANS_RANDOM_CENTERS)
                    # Now convert back into uint8, and make original image
                    center = np.uint8(center)
                    res = center[label.flatten()]
                    res2 = res.reshape((postitImageTest.shape))
                    # cv2.imshow('res2',res2)

                    bmin = res2[..., 0].min()
                    gmin = res2[..., 1].min()
                    rmin = res2[..., 2].min()
                    if postit.colour == "ORANGE":
                        postitImage[np.where((res2 > [0, 0, 0]).all(axis=2))] = [0, 0, 0]
                        postitImage[np.where((res2 > [bmin, gmin, rmin]).all(axis=2))] = [26, 160, 255]
                    elif postit.colour == "YELLOW":
                        postitImage[np.where((res2 > [0, 0, 0]).all(axis=2))] = [0, 0, 0]
                        postitImage[np.where((res2 > [bmin, gmin, rmin]).all(axis=2))] = [93, 255, 237]
                    elif postit.colour == "BLUE":
                        postitImage[np.where((res2 > [0, 0, 0]).all(axis=2))] = [0, 0, 0]
                        postitImage[np.where((res2 > [bmin, gmin, rmin]).all(axis=2))] = [255, 200, 41]
                    elif postit.colour == "MAGENTA":
                        postitImage[np.where((res2 > [0, 0, 0]).all(axis=2))] = [0, 0, 0]
                        postitImage[np.where((res2 > [bmin, gmin, rmin]).all(axis=2))] = [182, 90, 255]
                    #cv2.imwrite("test.png",postitImageTest)
                    #print(pytesseract.image_to_string(Image.open("test.png")))


                    # cv2.imshow("debugC", postitImage)
                    # cv2.waitKey(0)
                    disp_image[y1:y1 + postitImage.shape[0], x1:x1 + postitImage.shape[1]] = postitImage
                    cv2.rectangle(disp_image,
                                  (x1, y1),
                                  (x1 + postitImage.shape[1], y1 + postitImage.shape[0]),
                                  (0, 200, 200),
                                  thickness=4)

            r = 720 / disp_image.shape[1]
            dim = (720, int(disp_image.shape[0] * r))

            # perform the actual resizing of the image and show it
            disp_image = cv2.resize(disp_image, dim, interpolation=cv2.INTER_AREA)
            cv2.imshow("Display", disp_image)
            cv2.waitKey(0)

    # ======================================================== #

    def move_postit(self, ID, new_x, new_y):
        # Get postit
        last_canvas = self.canvasList[-1]
        postit = last_canvas.get_postit(ID)
        # Change location
        postit.set_position(new_x, new_y)
        # Create new canvas
        self.new_id = uuid.uuid4()
        self.delete_binned()
        new_canvas = Canvas(image=self.raw_image,
                            canvasBounds=self.canvasBounds,
                            id=self.new_id,
                            postits=self.activePostits,
                            connections=self.postitConnections,
                            derivedFrom=self.prevCanvasID,
                            derivedAt=self.snapshot_time
                            )
        self.canvasConnections.append([self.prevCanvasID, self.new_id])
        self.prevCanvasID = self.new_id
        self.canvasList.append(new_canvas)

if __name__ == "__main__":
    ######
    # When Using this test code follow these steps to minimize problems with image processing
    # 1.    Set backgroundend_point of projector to white
    # 2.    Run this script
    # 3.    Add initial postits
    # 4.    Cover the projector and pess enter with the console selected
    # 5.    Drag the "Display" window to be shown on projector, and uncover projector. Do not close this window
    # 6.    Make changes to postit layout
    # 7.    Cover the projector and pess enter, this time with the "Display" window selected
    # 8.    Uncover projector
    # 9.    If expected postits are missing
    #           goto Deubug.
    # 10.   Else goto 6.
    #
    # Debug:
    #   - Area being cropped out as the canvas is not correct
    #       ~ Cause : Brightness in the room differs from test conditions
    #       ~ Fix   : Change find canvas threshold
    #   - Postit not found
    #       ~ Cause : Brightness in the room differs from test conditions
    #       ~ Fix   : Change find postit threshold
    #####

    canvImg = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154758.jpg')
    boardModel = Model()
    boardModel.set_debug(state=False)
    boardModel.new_calib_image(image=canvImg)
    boardModel.run_auto_calibrate(show_debug=False)
    boardModel.image_settings(mipa=9000, mapa=20000, lento=0.4, sig=0.33, mico=64, maco=200, poth=120)
    for idx in range(0,len(os.listdir ('/home/jjs/projects/Minority-Report/src/testImg/'))):
        image = cv2.imread('/home/jjs/projects/Minority-Report/src/testImg/' + str(idx) + '.png')
        boardModel.new_raw_image(image=image, time=datetime.datetime.now(), update=1)
        boardModel.display()
    boardModel.move_postit(boardModel.canvasList[-1].postits[0].id, 500, 500)
    boardModel.display()

    # boardModel = Model()
    # boardModel.set_debug(state=False)
    # boardModel.image_settings(mipa=5000, mapa=40000, lento=0.2, sig=0.33, mico=64, maco=200, poth=105)
    # #input("Waiting for focus >")
    # #requests.get("http://localhost:8080/focus")
    # input("Waiting for boarders>")
    # r = requests.get("http://localhost:8080") # Request image from phone
    # # Receiving an image from the request gives code 200, all other returns means that the image has no been obtained
    # if r.status_code == 200:
    #     print("Got Good Calibartion Image")
    #     nparray = np.asarray(bytearray(r.content), dtype="uint8") # Transform byte array to numpy array
    #     canvImg = cv2.imdecode(nparray,cv2.IMREAD_COLOR) # Decode values as openCV colours
    #     boardModel.new_calib_image(image=canvImg) #set as calibration image
    #     boardModel.run_auto_calibrate() # Autocalibratefrom image
    # else:
    #     print(":( Got Bad Calibration Image")
    #     print(r.text)
    # input("Waiting >")
    # while(1):
    #     r = requests.get("http://localhost:8080")
    #     if r.status_code == 200:
    #         print("Got Good Postit Image")
    #         nparray = np.asarray(bytearray(r.content), dtype="uint8")
    #         img = cv2.imdecode(nparray,cv2.IMREAD_COLOR)
    #         boardModel.new_raw_image(img, datetime.datetime.now(),update=1)
    #         boardModel.display()
    #     else:
    #         print(":( Got Bad Postit Image")
    #         print(r.text)
