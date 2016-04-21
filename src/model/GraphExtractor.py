import cv2
import numpy as np
import math
import pytesseract
from PIL import Image

class GraphExtractor:
    """Get postits from a board image"""
    def __init__(self, image, previousPostits):
        self.DEBUG_PLOT = False
        self.rawImage = image
        self.prevPostits = previousPostits
        self.image = image
        self.postitPos = []
        self.postitPts = []
        self.postitImage = []
        self.postitColour = []
        self.lineEnds = []

        self.ColourThresholds = {
            "ORANGE": {
                "min_rg": 0,
                "max_rg": 70,
                "min_rb": 60,
                "max_rb": 150,
                "min_gb": 25,
                "max_gb": 100
            },
            "YELLOW": {
                "min_rg": -30,
                "max_rg": 15,
                "min_rb": 35,
                "max_rb": 120,
                "min_gb": 40,
                "max_gb": 125
            },
            "BLUE": {
                "min_rg": -80,
                "max_rg": -20,
                "min_rb": -120,
                "max_rb": -40,
                "min_gb": -45,
                "max_gb":   0
            },
            "MAGENTA": {
                "min_rg": 40,
                "max_rg": 135,
                "min_rb": 25,
                "max_rb": 90,
                "min_gb": -55,
                "max_gb": -10
            },
        }

    def extractGraph(self, showDebug, minPostitArea, maxPostitArea, lenTolerence, minColourThresh, maxColourThresh, postitThresh):
        postits = self.extractPostits(showDebug, minPostitArea, maxPostitArea, lenTolerence, minColourThresh, maxColourThresh, postitThresh)
        lines =  self.extractLines(postits, showDebug)
        graph = {
                "postits": postits,
                "lines": lines
            }
        return graph

    def extractPostits(self, showDebug, minPostitArea, maxPostitArea, lenTolerence, minColourThresh, maxColourThresh, postitThresh):

        foundPostits = []
        img = self.image
        boxedimg = img.copy()
        testimg1 = img.copy()

        # kernel = np.ones((3,3),np.uint8)
        # testimg1 = cv2.dilate(testimg1,kernel,iterations = 3)
        # testimg2 = cv2.dilate(testimg2,kernel,iterations = 3)
        # self.display("debug",testimg2)
        # testimg1[:,:,0] = testimg2[:,:,0]-(0.1*testimg2[:,:,1]+0.1*testimg2[:,:,2])
        # testimg1[:,:,1] = testimg2[:,:,1]-(0.1*testimg2[:,:,0]+0.1*testimg2[:,:,2])
        # testimg1[:,:,2] = testimg2[:,:,2]-(0.1*testimg2[:,:,1]+0.1*testimg2[:,:,0])
        # testimg2[np.where((testimg1 > 90).all(axis=2))] = [0,0,0]
        # self.display("debug",testimg1)
        # self.display("debug",testimg2)

        #edgegray = self.edge(testimg1, False, showDebug, postitThresh)

        newimg = cv2.cvtColor(testimg1,cv2.COLOR_BGR2HSV)
        satmax = newimg[..., 0].max()
        satmin = newimg[..., 0].min()
        satthresh = ((100/256)*(satmax-satmin))+satmin
        print(satthresh)
        newimg[np.where((newimg < [255,satthresh,255]).all(axis=2))] = [0,0,0]
        newimg = cv2.cvtColor(newimg,cv2.COLOR_HSV2BGR)
        #self.display("debug",newimg)
        gray = cv2.cvtColor(newimg, cv2.COLOR_BGR2GRAY)
        edgegray = cv2.Canny(gray, 1, 30)

        #self.display("debug",edgegray)
        (_,cnts, _) = cv2.findContours(edgegray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for c in cnts:
            box = cv2.boxPoints(cv2.minAreaRect(c))
            box = np.int0(box)
            cv2.drawContours(boxedimg, [box], 0, (0, 255, 0), 3)
            if showDebug:
                print(cv2.contourArea(box))
                cv2.imshow("Debug",boxedimg)
            if ((cv2.contourArea(box) > minPostitArea) and (cv2.contourArea(box) < maxPostitArea)):
                #print("here")
                length = math.hypot(box[0,0]-box[1,0], box[0,1]-box[1,1])
                height = math.hypot(box[2,0]-box[1,0], box[2,1]-box[1,1])
                if (length*(2-lenTolerence) < length+height < length*(2+lenTolerence)):
                    Rectangle = cv2.boundingRect(c)

                    fContour = c.flatten()
                    canvX = np.zeros([int(len(fContour)/2),1])
                    canvY = np.zeros([int(len(fContour)/2),1])
                    l1 = np.zeros(int(len(fContour)/2))
                    l2 = np.zeros(int(len(fContour)/2))
                    l3 = np.zeros(int(len(fContour)/2))
                    l4 = np.zeros(int(len(fContour)/2))
                    for i in range(0,len(fContour),2):
                        canvX[int(i/2)] =  fContour[i]
                        canvY[int(i/2)] =  fContour[i+1]
                    xmax = np.max(canvX)
                    ymax = np.max(canvY)
                    xmin = np.min(canvX)
                    ymin = np.min(canvY)
                    for n in range(0,len(canvX)):
                        lx = ((canvX[n]-xmin) / (xmax-xmin))
                        ly = ((canvY[n]-ymin) / (ymax-ymin))
                        l1[n] = lx+ly
                        l2[n] = (1-lx)+ly
                        l3[n] = lx+(1-ly)
                        l4[n] = (1-lx)+(1-ly)
                    max1 = np.argmax(l1)
                    max2 = np.argmax(l2)
                    max3 = np.argmax(l3)
                    max4 = np.argmax(l4)
                    #print(str(canvX[max1])+","+str(canvY[max1]))
                    #print(str(canvX[max2])+","+str(canvY[max2]))
                    #print(str(canvX[max3])+","+str(canvY[max3]))
                    #print(str(canvX[max4])+","+str(canvY[max4]))
                    postitPts = [(canvX[max1][0], canvY[max1][0]), (canvX[max2][0], canvY[max2][0]), (canvX[max3][0], canvY[max3][0]), (canvX[max4][0], canvY[max4][0])]

                    postitimg = self.four_point_transform(img,np.array(postitPts))
                    #cv2.imshow("debug", postitimg)
                    #cv2.waitKey(0)
                    self.postitPts.append(np.array(postitPts))
                    self.postitImage.append(postitimg)

                    self.postitPos.append(Rectangle)
                    #self.postitImage.append(img[Rectangle[1]:(Rectangle[1]+Rectangle[3]), Rectangle[0]:(Rectangle[0]+Rectangle[2])])
                    #self.display("name",self.postitImage[-1])

        for idx, postit in enumerate(self.postitImage):

            gray = cv2.cvtColor(postit, cv2.COLOR_BGR2GRAY)
            rTotal = gTotal = bTotal = 0
            count = 0
            #print(postit.shape)
            (width, height, depth) = postit.shape
            for y in range(height):
                for x in range(width):
                    if minColourThresh < gray[x,y] < maxColourThresh:
                        b, g, r = postit[x,y]
                        rTotal += r
                        gTotal += g
                        bTotal += b

            count = width * height

            rAvg = rTotal / count
            gAvg = gTotal / count
            bAvg = bTotal / count

            guessedColour = self.guess_colour(rAvg, gAvg, bAvg)
            if guessedColour != None:
                self.postitColour.append(guessedColour)

                foundPostit = {
                    "image": postit,
                    "colour": guessedColour,
                    "position": self.postitPos[idx],
                    "points": self.postitPts[idx]
                }
                foundPostits.append(foundPostit)

        return foundPostits

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

    def guess_colour(self, r, g, b):
        r = int(r)
        g = int(g)
        b = int(b)
        rg = r - g
        rb = r - b
        gb = g - b
        for colour in self.ColourThresholds:
            if ((rg >= self.ColourThresholds[colour]["min_rg"]) and
                    (rg <= self.ColourThresholds[colour]["max_rg"]) and
                    (rb >= self.ColourThresholds[colour]["min_rb"]) and
                    (rb <= self.ColourThresholds[colour]["max_rb"]) and
                    (gb >= self.ColourThresholds[colour]["min_gb"]) and
                    (gb <= self.ColourThresholds[colour]["max_gb"])):
                return colour

        return None

    def extractLines(self, postits, showDebug):
        foundLines = []
        img = self.image

        edged = self.edge(img, True, showDebug, 0)

        (_,cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        tolerence =40
        for c in cnts:
            postitIdx = [-1,-1]
            postitIdStart = 0
            postitIdEnd = 0

            startPoint, endPoint = self.findFurthestPair(c)

            for idx, postit in enumerate(postits):
                if postit["position"][0]-tolerence < startPoint[0] < postit["position"][0]+postit["position"][2]+tolerence and postit["position"][1]-tolerence < startPoint[1] < postit["position"][1]+postit["position"][3]+tolerence:
                    postitIdx[0] = idx
                if postit["position"][0]-tolerence < endPoint[0] < postit["position"][0]+postit["position"][2]+tolerence and postit["position"][1]-tolerence < endPoint[1] < postit["position"][1]+postit["position"][3]+tolerence:
                    postitIdx[1] = idx

            for idx, postit in enumerate(self.prevPostits):
                if not postit.physical:
                    if postit.get_position()[0]-tolerence < startPoint[0] < postit.get_position()[0]+postit.get_size()[0]+tolerence and postit.get_position()[1]-tolerence < startPoint[1] < postit.get_position()[1]+postit.get_size()[1]+tolerence:
                        postitIdStart = postit.get_id()
                    if postit.get_position()[0]-tolerence < endPoint[0] < postit.get_position()[0]+postit.get_size()[0]+tolerence and postit.get_position()[1]-tolerence < endPoint[1] < postit.get_position()[1]+postit.get_size()[1]+tolerence:
                        postitIdEnd = postit.get_id()


            if postitIdStart and postitIdEnd:
                foundLine = {
                        "postitIdStart": postitIdStart,
                        "postitIdEnd": postitIdEnd
                        }
                foundLines.append(foundLine)
            elif postitIdStart and postitIdx[1] > -1:
                foundLine = {
                        "postitIdStart": postitIdStart,
                        "postitIdx": postitIdx
                        }
                foundLines.append(foundLine)
            elif postitIdEnd and postitIdx[0] > -1:
                foundLine = {
                        "postitIdEnd": postitIdEnd,
                        "postitIdx": postitIdx
                        }
                foundLines.append(foundLine)
            elif postitIdx[0] > -1 and postitIdx[1] > -1 and postitIdx[0] != postitIdx[1]:
                if not foundLines:
                    foundLine = {
                        "postitIdx": postitIdx
                        }
                    foundLines.append(foundLine)
        return foundLines

    def findFurthestPair(self, contour):
        distList =  np.zeros((4,4))

        leftmost = tuple(contour[contour[:,:,0].argmin()][0])
        rightmost = tuple(contour[contour[:,:,0].argmax()][0])
        topmost = tuple(contour[contour[:,:,1].argmin()][0])
        bottommost = tuple(contour[contour[:,:,1].argmax()][0])
        points = [leftmost, rightmost, topmost, bottommost]

        for idxa, pointa in enumerate(points):
            for idxb, pointb in enumerate(points):
                distList[idxa, idxb,] = math.hypot(pointa[0]-pointb[0],pointa[1]-pointb[1])
        maxDistIdx = np.argmax(distList, axis=None)
        maxDistIdx = np.unravel_index(maxDistIdx, distList.shape)
        start = points[maxDistIdx[0]]
        end = points[maxDistIdx[1]]
        return(start, end)

    def edge(self,img,line, showDebug, thresh):
        kernel = np.ones((5,5),np.uint8)
        img = cv2.medianBlur(img,9)
        #if showDebug:
        #   self.display("blurred",img)
        if not line:
            img = cv2.dilate(img,kernel,iterations = 3)
            self.display("debug",img)
            imgcopy = img.copy()
            __,img = cv2.threshold(imgcopy,thresh,255,cv2.THRESH_BINARY)
            self.display("debug",img)

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        #if showDebug:
        #    self.display("gray",gray)

        edged = cv2.Canny(gray, 1, 30)
        if showDebug:
            self.display("debug", edged)

        return edged

    def display(self,name,img):
        img = cv2.resize(img,None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        cv2.imshow(name, img)
        cv2.waitKey(0)



def findCanvas(image, showDebug=False):

    (__, board) = cv2.threshold(image,100,255,cv2.THRESH_TOZERO)
    grayBoard = cv2.cvtColor(board, cv2.COLOR_RGB2GRAY)



    (__, boardContours, __) = cv2.findContours(grayBoard, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in boardContours]

    max_index = np.argmax(areas)
    canvasContour = boardContours[max_index]
    canvasBounds = cv2.boundingRect(canvasContour)

    if showDebug:
        for c in boardContours:
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(image,[box],0,(0,0,255),2)

        cv2.waitKey(0)

    return canvasBounds


if __name__ == "__main__":
    canvImg = cv2.imread("IMG_20160304_154758.jpg")
    canvArea = findCanvas(canvImg)
    image1 = cv2.imread("IMG_20160304_154813.jpg")
    image1 = image1[canvArea[1]:(canvArea[1]+canvArea[3]), canvArea[0]:(canvArea[0]+canvArea[2])]
    image2 = cv2.imread("IMG_20160304_154821.jpg")
    image2 = image2[canvArea[1]:(canvArea[1]+canvArea[3]), canvArea[0]:(canvArea[0]+canvArea[2])]

    extractor1 = GraphExtractor(image1)
    graph1 = extractor1.extractGraph(minPostitArea = 10000, maxPostitArea = 40000, lenTolerence = 0.4, sigma=0.33)

    extractor2 = GraphExtractor(image2)
    graph2 = extractor2.extractGraph(minPostitArea = 10000, maxPostitArea = 40000, lenTolerence = 0.4, sigma=0.33)

    for postit in graph1["postits"]:
        x1 = postit["position"][0]
        y1 = postit["position"][1]
        x2 = postit["position"][0]+postit["position"][2]
        y2 = postit["position"][1]+postit["position"][3]
        cv2.rectangle(image1,(x1,y1),(x2,y2),(0,255,0),thickness=4)
    for line in graph1["lines"]:
        cv2.line(image1, line["startPoint"], line["endPoint"], [255,0,0], thickness=4)
    for postit in graph2["postits"]:
        x1 = postit["position"][0]
        y1 = postit["position"][1]
        x2 = postit["position"][0]+postit["position"][2]
        y2 = postit["position"][1]+postit["position"][3]
        cv2.rectangle(image2,(x1,y1),(x2,y2),(0,255,0),thickness=4)
    for line in graph2["lines"]:
        cv2.line(image2, line["startPoint"], line["endPoint"], [255,0,0], thickness=4)

    bf = cv2.BFMatcher()
    postitPair = []
    for o,postit1 in enumerate(graph1["postits"]):
        for p,postit2 in enumerate(graph2["postits"]):
            matches = bf.knnMatch(postit1["descriptors"], postit2["descriptors"], k = 2)
            good = []
            for m,n in matches:
                if m.distance < 0.45*n.distance:
                    good.append([m])
            #print(o,p, len(good))
            if (len(good)>5):
                postitPair.append([o,p])
                gray = cv2.cvtColor(postit1["image"], cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray,(3,3),0)
                ret,threshed = cv2.threshold(gray,127,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
                kernel = np.ones((3,3),np.uint8)
                threshed = cv2.dilate(threshed,kernel)
                print(pytesseract.image_to_string(Image.open("postit.png")))
    print(postitPair)

    extractor1.display("canvas1",image1)
    extractor2.display("canvas2",image2)

#http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_feature2d/py_feature_homography/py_feature_homography.html


