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

    def extractPostits(self, sigma=0.8, minPostitArea = 3000, maxPostitArea = 20000, lenTolerence = 0.15, minColourThresh = 64, maxColourThresh = 200):
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
                if (length*2-lenTolerence < length+height < length*2+lenTolerence):
                    Rectangle = cv2.boundingRect(c)
                    self.postitPos.append(Rectangle)
                    self.postitImage.append(self.image[Rectangle[1]:(Rectangle[1]+Rectangle[3]), Rectangle[0]:(Rectangle[0]+Rectangle[2])])
        for postit in self.postitImage:
            gray = cv2.cvtColor(postit, cv2.COLOR_BGR2GRAY)
            rTotal = gTotal = bTotal = 0
            count = 0
            for y in range(postit.height):
                for x in range(postit.width):
                    if minColourThresh < gray[x,y] < maxColourThresh:
                        b, g, r = postit[x,y]
                        rTotal += r
                        gTotal += g
                        bTotal += b

            count = postit.width * postit.height

            rAvg = rTotal / count
            gAvg = gTotal / count
            bAvg = bTotal / count
        self.postitColour.append(self.guess_colour(rAvg, gAvg, bAvg))




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



