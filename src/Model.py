import cv2
import numpy as np
from src.GraphExtractor import GraphExtractor
from src.Canvas import Canvas

class Model:
    """Current Canvas and history"""
    def __init__(self):
        self.currentCanvasBounds = []
        self.CanvasList = []
        self.rawImage = []
#=========================================================#
    def getRawImage(self):
        pass

    def getCanvasBounds(self):
        return self.currentCanvasBounds

    def setCanvasBounds(self):
        pass

    def runAutoCalibrate(self):
        self.currentCanvasBounds = self.findCanvas(self.rawImage)

    def getAbstractGraph(self):
        pass

    def getCanvas(self,ID):
        pass

    def save(self,filename):
        pass

    def load(self,filename):
        pass
#========================================================#
    def newRawImage(self,image):
        self.rawImage = image

    def findCanvas(self, image, showDebug=False):

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

    def update(self):
        pass

if __name__ == "__main__":
    canvImg = cv2.imread("IMG_20160304_154758.jpg")
    boardModel = Model()
    boardModel.newRawImage(canvImg)
    boardModel.runAutoCalibrate()
    print(boardModel.getCanvasBounds())

