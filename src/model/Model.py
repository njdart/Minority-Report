import cv2
import numpy as np
import uuid
import json
from src.model.GraphExtractor import GraphExtractor
from src.model.Canvas import Canvas
from src.model.Postit import Postit

class Model:
    """Model of the board storing history of the canvas and settings used to ge extract that information"""
    def __init__(self):
        self.canvasList = []
        self.canvasConnections = []

        self.calibImage = []

        self.canvasBounds = []
        self.rawImage = []
        self.activePostits = []
        self.postitConnections = []
#=========================================================#
    # Return current rawImage
    def getRawImage(self):
        return self.rawImage

    # Return current canvasBounds
    def getCanvasBounds(self):
        return self.canvasBounds

    # Change canvas bounds for when the auto-generated bounds are wrong
    def setCanvasBounds(self, newBounds):
        self.canvasBounds = newBounds

    # From the current calibImage calculates likely boundaries of the canvas
    def runAutoCalibrate(self):
        self.canvasBounds = self.findCanvas(self.calibImage)

    # todo: Returns position of postits and relationships of current graph
    def getAbstractGraph(self):
        pass

    # todo: Return canvas from history using the UUID associated with it
    def getCanvas(self,ID):
        pass

    # todo: Create JSON from the canvas history
    def save(self,filename):
        pass

    # todo: set canvas history from JSON file
    def load(self,filename):
        pass
#========================================================#

    # Set a new calibImage
    def newCalibImage(self,image):
        self.calibImage = image

    # Set a new rawImage
    def newRawImage(self,image,time):
        self.rawImage = image
        self.snapshotTime = time
        self.update()

    # From calibImage find likely canvasBounds
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

    # Using canvasBounds on rawImage extract an image of the canvas
    def getCanvasImage(self):
        canvasStartX = self.canvasBounds[0]
        canvasStartY = self.canvasBounds[1]
        canvasEndX = self.canvasBounds[0]+self.canvasBounds[2]
        canvasEndY = self.canvasBounds[1]+self.canvasBounds[3]
        return self.rawImage[canvasStartY:canvasEndY, canvasStartX:canvasEndX]

    # Compre current graph with previous graph
    def comparePrev(self,newGraph):
        postitIDs = self.updatePostits(newGraph["postits"])
        self.updateLines(postitIDs,newGraph["lines"])

    # Compare a new list of postits to the list of known active postits
    def updatePostits(self,newPostits):
        bf = cv2.BFMatcher()
        postitIDs = [len(newPostits)]
        activePostitsFound = []
        for o,newPostit in enumerate(newPostits):
            goodMatches = []
            for p, oldPostit in enumerate(self.activePostits):
                matches = bf.knnMatch(oldPostit.descriptors, newPostit["descriptors"], k = 2)
                good = []
                for m,n in matches:
                    if m.distance < 0.45*n.distance:
                        good.append([m])
                #print(o,p, len(good))
                if (len(good)>5):
                    goodMatches.append(p)
                    activePostitsFound.append(oldPostit.ID)
            if (len(goodMatches) == 0):
                # Create new entry on list of active postits and then add ID to list
                newID = uuid.uuid4()
                createdPostit = Postit(newID,newPostit,'physical')
                self.activePostits.append(createdPostit)
                postitIDs.append(newID)
                activePostitsFound.append(newID)
            elif(len(goodMatches) == 1):
                # Return ID of Matched postits
                updatingPostit = self.activePostits.pop(goodMatches[0])
                postitIDs.insert(p, updatingPostit.getID())
                updatingPostit.update(newPostit)
                self.activePostits.append(updatingPostit)
            else:
                # Throw error as this state should not be reachable
                pass
        for p, oldPostit in enumerate(self.activePostits):
            if oldPostit.ID not in activePostitsFound:
                oldPostit.setState('digital')


        return postitIDs

    # Compare lines found with know list of connections
    def updateLines(self,postitIDs, lines):
        for cxn in lines:
            connection = [postitIDs[cxn[0]],postitIDs[cxn[0]]]
            if connection not in self.postitConnections:
                self.postitConnections.append(connection)

    # Main update loop using the current settings to extract data from current rawImage
    def update(self):
        canvasImage = self.getCanvasImage()
        extractor = GraphExtractor(canvasImage)
        graph = extractor.extractGraph(minPostitArea = 10000, maxPostitArea = 40000, lenTolerence = 0.4, sigma=0.33)
        self.comparePrev(graph)
        newCanvas = Canvas(uuid.uuid4(),self.snapshotTime,self.rawImage,self.canvasBounds,self.activePostits,self.postitConnections)
        self.canvasList.append(newCanvas)




if __name__ == "__main__":
    canvImg = cv2.imread("IMG_20160304_154758.jpg")
    boardModel = Model()
    boardModel.newCalibImage(canvImg)
    boardModel.runAutoCalibrate()
    image1 = cv2.imread("IMG_20160304_154813.jpg")
    boardModel.newRawImage(image1)
    image2 = cv2.imread("IMG_20160304_154821.jpg")
    boardModel.newRawImage(image2)


