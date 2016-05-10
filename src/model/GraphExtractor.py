import cv2
import numpy as np
import math
import pytesseract
from PIL import Image


class GraphExtractor:
    """
    Get postits from a board image
    """

    def __init__(self, image, previous_postits):
        self.DEBUG_PLOT = False
        self.rawImage = image
        self.prevPostits = previous_postits
        self.image = image
        self.postitPos = []
        self.postitPts = []
        self.postitImages = []
        self.postitColour = []
        self.lineEnds = []

        self.ColourThresholds = {
            "ORANGE": {
                "min_rg": 0,
                "max_rg": 90,
                "min_rb": 60,
                "max_rb": 160,
                "min_gb": 25,
                "max_gb": 100
            },
            "YELLOW": {
                "min_rg": -30,
                "max_rg": 15,
                "min_rb": 35,
                "max_rb": 140,
                "min_gb": 40,
                "max_gb": 140
            },
            "BLUE": {
                "min_rg": -110,
                "max_rg": -20,
                "min_rb": -140,
                "max_rb": -40,
                "min_gb": -45,
                "max_gb": 0
            },
            "MAGENTA": {
                "min_rg": 40,
                "max_rg": 135,
                "min_rb": 25,
                "max_rb": 100,
                "min_gb": -55,
                "max_gb": -10
            },
        }

    # Extracts a representation of the canvas
    def extract_graph(self,
                      show_debug,
                      min_postit_area,
                      max_postit_area,
                      len_tolerence,
                      min_colour_thresh,
                      max_colour_thresh):
        postits = self.extract_postits(show_debug=show_debug,
                                       min_postit_area=min_postit_area,
                                       max_postit_area=max_postit_area,
                                       len_tolerence=len_tolerence,
                                       min_colour_thresh=min_colour_thresh,
                                       max_colour_thresh=max_colour_thresh)
        lines = self.extract_lines(postits=postits,
                                   show_debug=show_debug)
        graph = {
            "postits": postits,
            "lines": lines
        }
        return graph

    # Extracts a representation of the postits
    def extract_postits(self,
                        show_debug,
                        min_postit_area,
                        max_postit_area,
                        len_tolerence,
                        min_colour_thresh,
                        max_colour_thresh):

        found_postits = []
        img = self.image
        boxedimg = img.copy()
        testimg1 = img.copy()

        newimg = cv2.cvtColor(testimg1, cv2.COLOR_BGR2HSV)
        satthresh = 80
        # print(satthresh)
        newimg[np.where((newimg < [255, satthresh, 255]).all(axis=2))] = [0, 0, 0]
        newimg = cv2.cvtColor(newimg, cv2.COLOR_HSV2BGR)
        newimg[np.where((newimg < [80, 80, 80]).all(axis=2))] = [0, 0, 0]
        #display("debug", newimg)
        gray_img = cv2.cvtColor(newimg, cv2.COLOR_BGR2GRAY)
        edgegray = cv2.Canny(gray_img, 1, 30)
        #display("debug",edgegray)
        (_, cnts, _) = cv2.findContours(edgegray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for c in cnts:
            box = cv2.boxPoints(cv2.minAreaRect(c))
            box = np.int0(box)
            cv2.drawContours(boxedimg, [box], 0, (0, 255, 0), 3)
            # print(cv2.contourArea(box))
            if show_debug:
                print(cv2.contourArea(box))
                cv2.imshow("Debug", boxedimg)
            if (cv2.contourArea(box) > min_postit_area) and (cv2.contourArea(box) < max_postit_area):
                length = math.hypot(box[0, 0] - box[1, 0], box[0, 1] - box[1, 1])
                height = math.hypot(box[2, 0] - box[1, 0], box[2, 1] - box[1, 1])
                if length * (2 - len_tolerence) < length + height < length * (2 + len_tolerence):
                    rectangle = cv2.boundingRect(c)

                    flat_contour = c.flatten()
                    canvx = np.zeros([int(len(flat_contour) / 2), 1])
                    canvy = np.zeros([int(len(flat_contour) / 2), 1])
                    l1 = np.zeros(int(len(flat_contour) / 2))
                    l2 = np.zeros(int(len(flat_contour) / 2))
                    l3 = np.zeros(int(len(flat_contour) / 2))
                    l4 = np.zeros(int(len(flat_contour) / 2))
                    for i in range(0, len(flat_contour), 2):
                        canvx[int(i / 2)] = flat_contour[i]
                        canvy[int(i / 2)] = flat_contour[i + 1]
                    xmax = np.max(canvx)
                    ymax = np.max(canvy)
                    xmin = np.min(canvx)
                    ymin = np.min(canvy)
                    for idx in range(0, len(canvx)):
                        lx = ((canvx[idx] - xmin) / (xmax - xmin))
                        ly = ((canvy[idx] - ymin) / (ymax - ymin))
                        l1[idx] = lx + ly
                        l2[idx] = (1 - lx) + ly
                        l3[idx] = lx + (1 - ly)
                        l4[idx] = (1 - lx) + (1 - ly)
                    max1 = np.argmax(l1)
                    max2 = np.argmax(l2)
                    max3 = np.argmax(l3)
                    max4 = np.argmax(l4)
                    postit_pts = [(canvx[max1][0], canvy[max1][0]),
                                  (canvx[max2][0], canvy[max2][0]),
                                  (canvx[max3][0], canvy[max3][0]),
                                  (canvx[max4][0], canvy[max4][0])]

                    postitimg = self.four_point_transform(img, np.array(postit_pts))
                    if show_debug:
                        cv2.imshow("debug", postitimg)
                        cv2.waitKey(0)
                    self.postitPts.append(np.array(postit_pts))
                    self.postitImages.append(postitimg)
                    self.postitPos.append(rectangle)

        for idx, postit_image in enumerate(self.postitImages):

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

            guessed_colour = self.guess_colour(red_average, green_average, blue_average)
            # print(guessed_colour)
            if guessed_colour is not None:
                self.postitColour.append(guessed_colour)
                self.postitPts[idx] = self.order_points(self.postitPts[idx])
                found_postit = {
                    "image": postit_image,
                    "colour": guessed_colour,
                    "position": self.postitPos[idx],
                    "points": self.postitPts[idx]
                }
                found_postits.append(found_postit)

        return found_postits

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

    # Given total rgb of an image guess the colour
    def guess_colour(self, r, g, b):
        r = int(r)
        g = int(g)
        b = int(b)

        rg = r - g
        rb = r - b
        gb = g - b
        # print(rg)
        # print(rb)
        # print(gb)
        for colour in self.ColourThresholds:
            if ((rg >= self.ColourThresholds[colour]["min_rg"]) and
                    (rg <= self.ColourThresholds[colour]["max_rg"]) and
                    (rb >= self.ColourThresholds[colour]["min_rb"]) and
                    (rb <= self.ColourThresholds[colour]["max_rb"]) and
                    (gb >= self.ColourThresholds[colour]["min_gb"]) and
                    (gb <= self.ColourThresholds[colour]["max_gb"])):
                return colour

        return None

    # Extracts a representation of the connections
    def extract_lines(self, postits, show_debug):
        found_lines = []
        img = self.image
        edged = self.edge(img, show_debug)
        (_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for c in cnts:
            if cv2.arcLength(c, True) > 300:
                array = []
                for index in range(0, len(c), 10):
                    contained = False
                    for idx, ipostit in enumerate(postits):
                        rectanglearea = self.get_area(ipostit["points"])
                        pointarea = self.get_area((ipostit["points"][0], ipostit["points"][1], c[index][0]))\
                                    + self.get_area((ipostit["points"][1], ipostit["points"][2], c[index][0]))\
                                    + self.get_area((ipostit["points"][2], ipostit["points"][3], c[index][0]))\
                                    + self.get_area((ipostit["points"][3], ipostit["points"][0], c[index][0]))
                        if pointarea < rectanglearea*1.1:
                                contained = True
                        if pointarea < rectanglearea*1.25 and not contained:
                            if not array:
                                array.append(idx)
                            elif idx is not array[-1]:
                                array.append(idx)


                    for idx, jpostit in enumerate(self.prevPostits):
                        if not jpostit.physical:
                            postitpoints = jpostit.get_points()
                            rectanglearea = self.get_area(postitpoints)
                            pointarea = self.get_area((postitpoints[0], postitpoints[1], c[index][0])) \
                                    + self.get_area((postitpoints[1], postitpoints[2], c[index][0]))\
                                    + self.get_area((postitpoints[2], postitpoints[3], c[index][0]))\
                                    + self.get_area((postitpoints[3], postitpoints[0], c[index][0]))
                            if pointarea < rectanglearea*1.1:
                                contained = True
                            if pointarea < rectanglearea*1.25 and not contained:
                                if not array:
                                    array.append(jpostit.get_id())
                                elif jpostit.get_id() is not array[-1]:
                                    array.append(jpostit.get_id())

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
                            found_line = {
                                "postitIdStart": postit_id_start,
                                "postitIdEnd": postit_id_end
                            }
                            found_lines.append(found_line)
                        elif postit_id_start and postit_idx[1] > -1:
                            found_line = {
                                "postitIdStart": postit_id_start,
                                "postitIdx": postit_idx
                            }
                            found_lines.append(found_line)
                        elif postit_id_end and postit_idx[0] > -1:
                            found_line = {
                                "postitIdEnd": postit_id_end,
                                "postitIdx": postit_idx
                            }
                            found_lines.append(found_line)
                        elif postit_idx[0] > -1 and postit_idx[1] > -1:
                            found_line = {
                                "postitIdx": postit_idx
                            }
                            found_lines.append(found_line)
        return found_lines

    # Find the pair of points in a contour that are furthest apart
    def find_furthest_pair(self, contour):
        distList = np.zeros((4, 4))

        leftmost = tuple(contour[contour[:, :, 0].argmin()][0])
        rightmost = tuple(contour[contour[:, :, 0].argmax()][0])
        topmost = tuple(contour[contour[:, :, 1].argmin()][0])
        bottommost = tuple(contour[contour[:, :, 1].argmax()][0])
        points = [leftmost, rightmost, topmost, bottommost]

        for idxa, pointa in enumerate(points):
            for idxb, pointb in enumerate(points):
                distList[idxa, idxb,] = math.hypot(pointa[0] - pointb[0], pointa[1] - pointb[1])
        maxDistIdx = np.argmax(distList, axis=None)
        maxDistIdx = np.unravel_index(maxDistIdx, distList.shape)
        start = points[maxDistIdx[0]]
        end = points[maxDistIdx[1]]
        return (start, end)

    # Smooth and then find the edges of an image
    def edge(self, img, show_debug):
        kernel = np.ones((5, 5), np.uint8)
        #img = cv2.medianBlur(img, 9)
        img = cv2.bilateralFilter(img,9,75,75)
        gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        edged = cv2.Canny(gray_image, 1, 30)
        if show_debug:
            display("debug", edged)

        return edged

    def get_area(self, points):
        #if len(points) == 4:
        #    points = self.order_points(points)
        pointsum = 0
        for index in range(-1, len(points) - 1):
            pointsum = pointsum + (points[index][0] * points[index + 1][1] - points[index][1] * points[index + 1][0])
        area = abs(pointsum / 2)
        return area


# Display image at half size
def display(name, img):
    img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    cv2.imshow(name, img)
    cv2.waitKey(0)


# Find canvas for testing the above class in isolation
def find_canvas(image, show_debug=False):
    (__, board) = cv2.threshold(image, 100, 255, cv2.THRESH_TOZERO)
    gray_board = cv2.cvtColor(board, cv2.COLOR_RGB2GRAY)

    (__, board_contours, __) = cv2.findContours(gray_board, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in board_contours]

    max_index = np.argmax(areas)
    canvas_contour = board_contours[max_index]
    canvas_bounds = cv2.boundingRect(canvas_contour)

    if show_debug:
        for c in board_contours:
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(image, [box], 0, (0, 0, 255), 2)

        cv2.waitKey(0)

    return canvas_bounds


if __name__ == "__main__":
    canvImg = cv2.imread("IMG_20160304_154758.jpg")
    canvArea = find_canvas(canvImg)
    image1 = cv2.imread("IMG_20160304_154813.jpg")
    image1 = image1[canvArea[1]:(canvArea[1] + canvArea[3]), canvArea[0]:(canvArea[0] + canvArea[2])]
    image2 = cv2.imread("IMG_20160304_154821.jpg")
    image2 = image2[canvArea[1]:(canvArea[1] + canvArea[3]), canvArea[0]:(canvArea[0] + canvArea[2])]
    activePostits = []

    extractor1 = GraphExtractor(image1, activePostits)
    graph1 = extractor1.extract_graph(show_debug=False,
                                      min_postit_area=10000,
                                      max_postit_area=40000,
                                      len_tolerence=0.4,
                                      min_colour_thresh=64,
                                      max_colour_thresh=200)

    extractor2 = GraphExtractor(image2, activePostits)
    graph2 = extractor2.extract_graph(show_debug=False,
                                      min_postit_area=10000,
                                      max_postit_area=40000,
                                      len_tolerence=0.4,
                                      min_colour_thresh=64,
                                      max_colour_thresh=200)

    for postit in graph1["postits"]:
        x1 = postit["position"][0]
        y1 = postit["position"][1]
        x2 = postit["position"][0] + postit["position"][2]
        y2 = postit["position"][1] + postit["position"][3]
        cv2.rectangle(image1, (x1, y1), (x2, y2), (0, 255, 0), thickness=4)
    for line in graph1["lines"]:
        cv2.line(image1, line["startPoint"], line["endPoint"], [255, 0, 0], thickness=4)
    for postit in graph2["postits"]:
        x1 = postit["position"][0]
        y1 = postit["position"][1]
        x2 = postit["position"][0] + postit["position"][2]
        y2 = postit["position"][1] + postit["position"][3]
        cv2.rectangle(image2, (x1, y1), (x2, y2), (0, 255, 0), thickness=4)
    for line in graph2["lines"]:
        cv2.line(image2, line["startPoint"], line["endPoint"], [255, 0, 0], thickness=4)

    bf = cv2.BFMatcher()
    postitPair = []
    for o, postit1 in enumerate(graph1["postits"]):
        for p, postit2 in enumerate(graph2["postits"]):
            matches = bf.knnMatch(postit1["descriptors"], postit2["descriptors"], k=2)
            good = []
            for m, n in matches:
                if m.distance < 0.45 * n.distance:
                    good.append([m])
            # print(o, p, len(good))
            if len(good) > 5:
                postitPair.append([o, p])
                gray = cv2.cvtColor(postit1["image"], cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (3, 3), 0)
                ret, threshed = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                kernel = np.ones((3, 3), np.uint8)
                threshed = cv2.dilate(threshed, kernel)
                print(pytesseract.image_to_string(Image.open("postit.png")))
    print(postitPair)

    display("canvas1", image1)
    display("canvas2", image2)
