import cv2
import numpy as np
import math

class PostitExtract:
    """Get postits from a board image"""
    def __init__(self, image):
        self.DEBUG_PLOT = False
        self.image = image
        self.postitPos = []
        self.postitImage = []
        self.postitColour = []

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

    def extractPostits(self, showDebug=False, sigma=0.8, minPostitArea = 3000, maxPostitArea = 20000, lenTolerence = 0.15, minColourThresh = 64, maxColourThresh = 200):
        
        foundPostits = []

        canvasPos = self.findCanvas()
        self.image = self.image[canvasPos[1]:(canvasPos[1]+canvasPos[3]), canvasPos[0]:(canvasPos[0]+canvasPos[2])]
        if showDebug:
            cv2.imshow("Canvas Extracted", self.image)
            cv2.waitKey(0)

        v = np.median(self.image)
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv2.Canny(self.image, lower, upper)

        (_,cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
        for c in cnts:
            box = cv2.boxPoints(cv2.minAreaRect(c))
            box = np.int0(box)
            if ((cv2.contourArea(box) > minPostitArea) and (cv2.contourArea(box) < maxPostitArea)):
                length = math.hypot(box[0,0]-box[1,0], box[0,1]-box[1,1])
                height = math.hypot(box[2,0]-box[1,0], box[2,1]-box[1,1])
                if (length*(2-lenTolerence) < length+height < length*(2+lenTolerence)):
                    Rectangle = cv2.boundingRect(c)
                    if showDebug:
                        print(cv2.contourArea(box))
                        cv2.drawContours(self.image, [box], 0, (0, 255, 0), 3)
                    self.postitPos.append(Rectangle)
                    self.postitImage.append(self.image[Rectangle[1]:(Rectangle[1]+Rectangle[3]), Rectangle[0]:(Rectangle[0]+Rectangle[2])])
        if showDebug:
            edged
            cv2.imshow("Canny edge detection", edged)
            cv2.imshow("Canvas Extracted", self.image)
            cv2.waitKey(0)

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
            self.postitColour.append(guessedColour)

            foundPostit = {
                "image": postit,
                "colour": guessedColour,
                "position": self.postitPos[idx]

            }

            foundPostits.append(foundPostit)

        return foundPostits

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

    def findCanvas(self):
        # cv2.imshow("Origonal", self.image)

        (__, board) = cv2.threshold(self.image,200,255,cv2.THRESH_TOZERO)
        grayBoard = cv2.cvtColor(board, cv2.COLOR_RGB2GRAY)
        
        # cv2.imshow("Gray Board", grayBoard)

        (__, boardContours, __) = cv2.findContours(grayBoard, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(c) for c in boardContours]

        max_index = np.argmax(areas)
        canvasContour=boardContours[max_index]
        canvasBounds = cv2.boundingRect(canvasContour)

        # temp = self.image.copy()

        # cv2.rectangle(temp,(canvasBounds[0],canvasBounds[1]),(canvasBounds[0]+canvasBounds[2],canvasBounds[1]+canvasBounds[3]),(0,255,0),2)

        # cv2.imshow("Canbas Bounds", temp)

        return canvasBounds

if __name__ == "__main__":
    image = cv2.imread("ks1.png")
    extractor = PostitExtract(image)
    postits = extractor.extractPostits(showDebug=False, minPostitArea = 800, maxPostitArea = 2000000, lenTolerence = 0.6)
    print(len(postits))
    num = 0
    for postit in postits:
        cv2.imshow("Postit %d" %(num),postit["image"])
        print(postit["colour"])
        print(postit["position"])
        num += 1
    cv2.waitKey(0)


