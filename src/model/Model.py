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
    """Model of the board storing history of the canvas and settings used to ge extract that information"""
    def __init__(self):
        self.canvasList = []
        self.canvasConnections = []
        self.prevCanvasID = None

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
    def runAutoCalibrate(self,canvThresh=150):
        self.canvasBounds = self.findCanvas(self.calibImage,canvThresh)

    # Returns position of postits and relationships of current graph
    def getAbstractGraph(self):
        positions = []
        IDs = []
        for postit in self.activePostits:
            positions.append(postit.location)
            IDs.append(postit.ID)

        postit = {
            "position" : positions,
            "ID" : IDs
        }
        graph = {
            "connections" : self.postitConnectionss,
            "postit" : postit
        }
        return graph

    # Return canvas from history using the UUID associated with it
    def getCanvas(self,ID):
        for postit in self.canvasList:
            if postit.ID == ID:
                return postit
        return None

    # Create JSON from the canvas history
    def save(self,filename):
        data = []
        zf = zipfile.ZipFile(filename+'.zip', mode='w')
        for canv in self.canvasList:
            cv2.imwrite(str(canv.ID)+".png",canv.rawImage)
            postits = []
            connections = []
            for canvPostit in canv.postits:
                postit = {
                    "colour" : canvPostit.colour,
                    "uuid" : str(canvPostit.ID),
                    "x" : canvPostit.location[0],
                    "y" : canvPostit.location[1],
                    "height": canvPostit.size[1],
                    "width": canvPostit.size[0],
                    "isPhysical" : canvPostit.physical
                }
                postits.append(postit)
            for cxn in canv.connections:
                connection = {
                    "from" : str(cxn[0]),
                    "to" : str(cxn[1]),
                    "type" : "line"

                }
                connections.append(connection)
            canvas={
               "uuid" : str(canv.ID),
                "derivedAt" : str(canv.timestamp),
                "derivedFrom" : str(canv.derivedFrom),
                "canvas": {
                    "top-left": {
                        "x": canv.bounds[0],
                        "y": canv.bounds[1]
                        },
                    "top-right": {
                        "x": canv.bounds[0]+canv.bounds[2],
                        "y": canv.bounds[1]
                        },
                    "bottom-left": {
                        "x": canv.bounds[0],
                        "y": canv.bounds[1]+canv.bounds[3]
                        },
                    "bottom-right": {
                        "x": canv.bounds[0]+canv.bounds[2],
                        "y": canv.bounds[1]+canv.bounds[3]
                        }
                    },
                "width" : canv.rawImage.shape[1],
                "height": canv.rawImage.shape[0],
                "postits" : postits,
                "connections" : connections
                }

            zf.write(str(canv.ID)+".png")
            os.remove(str(canv.ID)+".png")
            data.append(canvas)
        with open("canvas_history.json", 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=2, separators=(',',':'))
        zf.write("canvas_history.json")
        os.remove("canvas_history.json")
        zf.close()


    # set canvas history from JSON file
    def load(self,filename):
        zf = zipfile.ZipFile(filename+'.zip')
        data_file = zf.read("canvas_history.json").decode("utf-8")
        data =json.loads(data_file)
        for dataCanvas in data:
            image = zf.read(dataCanvas["uuid"]+".png")
            dataBoardImage =  cv2.imdecode(np.frombuffer(image, np.uint8), 1)
            dataBounds = [dataCanvas["canvas"]["top-left"]["x"], dataCanvas["canvas"]["top-left"]["y"],
                          dataCanvas["canvas"]["bottom-right"]["x"]-dataCanvas["canvas"]["top-left"]["x"],
                          dataCanvas["canvas"]["bottom-right"]["y"]-dataCanvas["canvas"]["top-left"]["y"]]
            dataPostits = []
            for dataPostit in dataCanvas["postits"]:
                postit = Postit(dataPostit["uuid"],dataPostit["x"],dataPostit["y"],dataPostit["width"],
                                dataPostit["height"],dataPostit["colour"],dataPostit["isPhysical"])
                dataPostits.append(postit)
            dataConnections = []
            for dataLine in dataCanvas["connections"]:
                cxn = [dataLine["from"],dataLine["to"]]
                dataConnections.append(cxn)

            canvas = Canvas(dataCanvas["uuid"],dataCanvas["derivedAt"],dataBoardImage,dataBounds,dataPostits,dataConnections,dataCanvas["derivedFrom"])
            self.canvasList.append(canvas)
        return None
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
    def findCanvas(self, image, thresh = 150, showDebug=False):
        (__, board) = cv2.threshold(image,thresh,255,cv2.THRESH_TOZERO)
        grayBoard = cv2.cvtColor(board, cv2.COLOR_RGB2GRAY)

        (__, boardContours, __) = cv2.findContours(grayBoard, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(c) for c in boardContours]

        max_index = np.argmax(areas)
        canvasContour = boardContours[max_index]
        canvasBounds = cv2.boundingRect(canvasContour)

        if showDebug:
            debugImage = image.copy()
            for c in boardContours:
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(debugImage,[box],0,(0,0,255),2)
            cv2.imshow("debug",debugImage)
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
        newUniquePostits = []
        for o,newPostit in enumerate(newPostits):
            goodMatches = []
            #print(len(self.activePostits))
            for p, oldPostit in enumerate(self.activePostits):
                matches = bf.knnMatch(oldPostit.getDescriptors(self.getCanvasImage()), newPostit["descriptors"], k = 2)
                good = []
                for m,n in matches:
                    if m.distance < 0.45*n.distance:
                        good.append([m])
                #print(o,p, len(good))
                if (len(good)>5):
                    #print("match")
                    goodMatches.append(p)
                    activePostitsFound.append(oldPostit.ID)
            if (len(goodMatches) == 0):
                # Create new entry on list of active postits and then add ID to list
                newID = uuid.uuid4()
                createdPostit =  Postit(newID, newPostit["position"][0], newPostit["position"][1],
                                        newPostit["position"][2], newPostit["position"][3], newPostit["colour"],True)
                newUniquePostits.append(createdPostit)
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

        self.activePostits.extend(newUniquePostits)
        for p, oldPostit in enumerate(self.activePostits):
            if oldPostit.ID not in activePostitsFound:
                oldPostit.setState(False)

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
        newCanvas = Canvas(newID, self.snapshotTime,self.rawImage,self.canvasBounds,self.activePostits,self.postitConnections,self.prevCanvasID)
        self.canvasConnections.append([self.prevCanvasID, newID])
        self.prevCanvasID = newID
        self.canvasList.append(newCanvas)

    def display(self):
        if len(self.canvasList):
            lastCanvas = self.canvasList[-1]
            dispImage = np.zeros((lastCanvas.bounds[3], lastCanvas.bounds[2], 3), np.uint8)
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
                    postitImage = postit.getImage(lastCanvas.getImage(self.rawImage))
                    dispImage[y1:y1+postitImage.shape[0], x1:x1+postitImage.shape[1]] = postitImage
                    cv2.rectangle(dispImage,(x1,y1),(x2,y2),(0,200,200),thickness=4)

            r = 1920 / dispImage.shape[1]
            dim = (1920, int(dispImage.shape[0] * r))

            # perform the actual resizing of the image and show it
            dispImage = cv2.resize(dispImage, dim, interpolation = cv2.INTER_AREA)
            cv2.imshow("Display", dispImage)
            cv2.waitKey(0)

if __name__ == "__main__":
    boardModel = Model()
    r = requests.get("http://localhost:8080")
    if r.status_code == 200:
        print("Got Good Calibartion Image")
        nparray = np.asarray(bytearray(r.content), dtype="uint8")
        canvImg = cv2.imdecode(nparray,cv2.IMREAD_COLOR)
        boardModel.newCalibImage(canvImg)
        boardModel.runAutoCalibrate(canvThresh=150)
    else:
        print(":( Got Bad Calibration Image")
        print(r.text)
    input("Waiting >")
    while(1):
        r = requests.get("http://localhost:8080")
        if r.status_code == 200:
            print("Got Good Postit Image")
            nparray = np.asarray(bytearray(r.content), dtype="uint8")
            img = cv2.imdecode(nparray,cv2.IMREAD_COLOR)
            boardModel.newRawImage(img, datetime.datetime.now())
            boardModel.display()
        else:
            print(":( Got Bad Postit Image")
            print(r.text)


    # canvImg = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154758.jpg')
    # boardModel = Model()
    # boardModel.newCalibImage(canvImg)
    # boardModel.runAutoCalibrate()
    # image1 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154813.jpg')
    # boardModel.newRawImage(image1, datetime.datetime.now())
    # #boardModel.display()
    # image2 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154821.jpg')
    # boardModel.newRawImage(image2, datetime.datetime.now())
    # #boardModel.display()
    # boardModel.save("canvas_data")
    # newBoard = Model()
    # newBoard.load("canvas_data")
    # newBoard.display()


