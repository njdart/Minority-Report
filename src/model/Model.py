import cv2
import numpy as np
import uuid
import json
import datetime
from src.model.GraphExtractor import GraphExtractor
from src.model.Canvas import Canvas
from src.model.Postit import Postit

class Model:
    """Model of the board storing history of the canvas and settings used to ge extract that information"""
    def __init__(self):
        self.canvasList = []
        self.canvasConnections = []
        self.prevCanvasID = 0

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
        data = self.canvasList
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

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
        postitIDs = []
        activePostitsFound = []
        for o,newPostit in enumerate(newPostits):
            goodMatches = []
            #print(len(self.activePostits))
            for p, oldPostit in enumerate(self.activePostits):
                matches = bf.knnMatch(oldPostit.descriptors, newPostit["descriptors"], k = 2)
                good = []
                for m,n in matches:
                    if m.distance < 0.40*n.distance:
                        good.append([m])
                #print(o,p, len(good))
                if (len(good)>5):
                    goodMatches.append(p)
                    activePostitsFound.append(oldPostit.ID)
            if (len(goodMatches) == 0):
                # Create new entry on list of active postits and then add ID to list
                newID = uuid.uuid4()
                createdPostit = Postit(newID,newPostit,0)
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
                oldPostit.setState(0)

        return postitIDs

    # Compare lines found with know list of connections
    def updateLines(self,postitIDs, lines):
        for cxn in lines:
            #print(cxn["postitIdx"][0])
            #print(postitIDs[cxn["postitIdx"][0]])
            connection = [postitIDs[cxn["postitIdx"][0]],postitIDs[cxn["postitIdx"][1]]]
            if connection not in self.postitConnections:
                self.postitConnections.append(connection)

    # Main update loop using the current settings to extract data from current rawImage
    def update(self):
        canvasImage = self.getCanvasImage()
        extractor = GraphExtractor(canvasImage)
        graph = extractor.extractGraph(minPostitArea = 10000, maxPostitArea = 40000, lenTolerence = 0.4, sigma=0.33)
        self.comparePrev(graph)
        newID = uuid.uuid4()
        newCanvas = Canvas(newID, self.snapshotTime,self.rawImage,self.canvasBounds,self.activePostits,self.postitConnections)
        self.canvasConnections.append([self.prevCanvasID, newID])
        self.prevCanvasID = newID
        self.canvasList.append(newCanvas)

    def display(self):
        dispImage = np.zeros((self.canvasBounds[3], self.canvasBounds[2], 3), np.uint8)
        lastCanvas = self.canvasList[-1]
        for line in lastCanvas.connections:
            startPoint = (int(lastCanvas.getPostit(line[0]).location[0]+(lastCanvas.getPostit(line[0]).size[0])/2), int(lastCanvas.getPostit(line[0]).location[1]+(lastCanvas.getPostit(line[0]).size[1])/2))
            endPoint = (int(lastCanvas.getPostit(line[1]).location[0]+(lastCanvas.getPostit(line[1]).size[0])/2), int(lastCanvas.getPostit(line[1]).location[1]+(lastCanvas.getPostit(line[1]).size[1])/2))
            cv2.line(dispImage, startPoint, endPoint, [255,0,0], thickness=4)
        for postit in lastCanvas.postits:
            x1 = postit.location[0]
            y1 = postit.location[1]
            x2 = postit.location[0]+postit.size[0]
            y2 = postit.location[1]+postit.size[1]
            if postit.physical == 1:
                cv2.rectangle(dispImage,(x1,y1),(x2,y2),(0,0,0),thickness=cv2.FILLED)
                cv2.rectangle(dispImage,(x1,y1),(x2,y2),(0,255,0),thickness=4)
            elif postit.physical == 0:
                cv2.rectangle(dispImage,(x1,y1),(x2,y2),(0,0,0),thickness=cv2.FILLED)
                dispImage[postit.location[0]:postit.location[0]+postit.image.shape[0], postit.location[1]:postit.location[1]+postit.image.shape[1]] = postit.image
                cv2.rectangle(dispImage,(x1,y1),(x2,y2),(0,200,200),thickness=4)

        r = 1920 / dispImage.shape[1]
        dim = (1920, int(dispImage.shape[0] * r))

        # perform the actual resizing of the image and show it
        dispImage = cv2.resize(dispImage, dim, interpolation = cv2.INTER_AREA)
        cv2.imshow("Display", dispImage)
        cv2.waitKey(0)

if __name__ == "__main__":
    canvImg = cv2.imread("IMG_20160304_154758.jpg")
    boardModel = Model()
    boardModel.newCalibImage(canvImg)
    boardModel.runAutoCalibrate()
    image1 = cv2.imread("IMG_20160304_154813.jpg")
    boardModel.newRawImage(image1, datetime.datetime.now())
    boardModel.display()
    image2 = cv2.imread("IMG_20160304_154821.jpg")
    boardModel.newRawImage(image2, datetime.datetime.now())
    #boardModel.save("data.txt")

