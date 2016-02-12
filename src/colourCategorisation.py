#!/usr/bin/env python3

from PIL import Image
import os

THRESHOLDS = {
    "ORANGE": {
        "min_rg": 0,
        "max_rg": 70,
        "min_rb": 60,
        "max_rb": 125,
        "min_gb": 25,
        "max_gb": 75
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
        "max_gb": -10
    },
    "MAGENTA": {
        "min_rg": 40,
        "max_rg": 100,
        "min_rb": 25,
        "max_rb": 60,
        "min_gb": -45,
        "max_gb": -10
    },
}

def guess_colour(r, g, b):
    r = int(r)
    g = int(g)
    b = int(b)
    rg = r - g
    rb = r - b
    gb = g - b
    for colour in THRESHOLDS:
        if ((rg >= THRESHOLDS[colour]["min_rg"]) and
                (rg <= THRESHOLDS[colour]["max_rg"]) and
                (rb >= THRESHOLDS[colour]["min_rb"]) and
                (rb <= THRESHOLDS[colour]["max_rb"]) and
                (gb >= THRESHOLDS[colour]["min_gb"]) and
                (gb <= THRESHOLDS[colour]["max_gb"])):
            return colour

    return None


if __name__ == "__main__":

    inputDir = "/tmp/postits"

    minThreshold = 64
    maxThreshold = 200

    for inputFile in os.listdir(inputDir):

        i = Image.open(os.path.join(inputDir, inputFile))

        grayScale = i.convert("L").getdata()

        rTotal = gTotal = bTotal = 0
        count = 0

        imgData = list(i.getdata())

        for y in range(i.height):
            for x in range(i.width):

                index = x + (y * i.width)

                if minThreshold < grayScale[index] < maxThreshold:
                    r, g, b = imgData[index]
                    rTotal += r
                    gTotal += g
                    bTotal += b

        count = i.width * i.height

        rAvg = rTotal / count
        gAvg = gTotal / count
        bAvg = bTotal / count

        # print('<div style="width: 100; height: 100; background-color: rgb' + str((int(rAvg), int(gAvg), int(bAvg))) + ';">' + inputFile + '</div>')
        print(inputFile + " " +  str(guess_colour(rAvg, gAvg, bAvg)))


