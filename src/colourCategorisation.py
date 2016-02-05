#!/usr/bin/env python3

from PIL import Image
import os

THRESHOLDS = {
    "LIME": {
        "min_red": 120,
        "max_red": 160,
        "min_green": 140,
        "max_green": 180,
        "min_blue": 70,
        "max_blue": 120
    },
    "ORANGE": {
        "min_red": 130,
        "max_red": 190,
        "min_green": 100,
        "max_green": 130,
        "min_blue": 40,
        "max_blue": 100
    },
    "YELLOW": {
        "min_red": 100,
        "max_red": 160,
        "min_green": 100,
        "max_green": 170,
        "min_blue": 50,
        "max_blue": 90
    },
    "BLUE": {
        "min_red": 10,
        "max_red": 100,
        "min_green": 90,
        "max_green": 130,
        "min_blue": 110,
        "max_blue": 180
    },
    "MAGENTA": {
        "min_red": 180,
        "max_red": 160,
        "min_green": 40,
        "max_green": 100,
        "min_blue": 80,
        "max_blue": 120
    },
}

def guess_colour(r, g, b):
    r = int(r)
    g = int(g)
    b = int(b)
    for colour in THRESHOLDS:
        if ((r >= THRESHOLDS[colour]["min_red"]) and
                (r <= THRESHOLDS[colour]["max_red"]) and
                (g >= THRESHOLDS[colour]["min_green"]) and
                (g <= THRESHOLDS[colour]["max_green"]) and
                (b >= THRESHOLDS[colour]["min_blue"]) and
                (b <= THRESHOLDS[colour]["max_blue"])):
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
        print(inputFile + str((int(rAvg), int(gAvg), int(bAvg))) + " " +  str(guess_colour(rAvg, bAvg, gAvg)))


