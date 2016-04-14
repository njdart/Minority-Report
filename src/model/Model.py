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

        self.minPostitArea = 2000
        self.maxPostitArea = 10000
        self.lenTolerence = 0.4
        self.minColourThresh = 64

        self.maxColourThresh = 200
        self.postitThresh = 120
        self.sigma = 0.33

        self.debug = False

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
    def runAutoCalibrate(self,showDebug=False):
        self.canvasBounds = self.findCanvas(self.calibImage, showDebug)

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
            "connections" : self.postitConnections,
            "postit" : postit
        }
        return graph

    # Return canvas from history using the UUID associated with it
    def getCanvas(self,ID):
        for canvas in self.canvasList:
            if canvas.ID == ID:
                return canvas
        return None

    # Create .zip archive of the canvas history
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
                    "isPhysical" : canvPostit.physical,
                    "lastCanvasID" : str(canvPostit.last_canvas_ID)
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

    # From .zip archive reconstruct the cavas history
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
                                dataPostit["height"],dataPostit["colour"],dataPostit["isPhysical"],dataPostit["lastCanvasID"])
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

    # Set a new rawImage triggering a new canvas to be taken
    def newRawImage(self,image,time,update = 0):
        self.rawImage = image
        self.snapshotTime = time
        if update:
            self.update()

    # From calibImage find likely canvasBounds
    def findCanvas(self, image, showDebug):
        smoothImg = self.bwSmooth(image)
        (__, grayBoard) = cv2.threshold(smoothImg,250,255,cv2.THRESH_OTSU)

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
            cv2.imshow("debug",cv2.resize(debugImage,None,fx=0.25,fy=0.25))
            #cv2.imshow("debug",debugImage)
            cv2.waitKey(0)

        return canvasBounds

    # Using canvasBounds on rawImage extract an image of the canvas
    def getCanvasImage(self):
        canvasStartX = self.canvasBounds[0]
        canvasStartY = self.canvasBounds[1]
        canvasEndX = self.canvasBounds[0]+self.canvasBounds[2]
        canvasEndY = self.canvasBounds[1]+self.canvasBounds[3]
        return self.rawImage[canvasStartY:canvasEndY, canvasStartX:canvasEndX]

    def getPrevCanvasImage(self, ID):
        if ID == self.newID:
            return self.getCanvasImage()
        else:
            canvas = self.getCanvas(ID)
            return canvas.getImage(canvas.rawImage)

    # Compare current graph with previous graph
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
            maxidx = -1
            good = np.zeros(len(self.activePostits), dtype=np.int)
            #print(len(self.activePostits))
            IDs = []
            for p, oldPostit in enumerate(self.activePostits):

                oim = self.bwSmooth(oldPostit.getImage(self.getPrevCanvasImage(oldPostit.last_canvas_ID)))
                nim = self.bwSmooth(newPostit["image"])
                # Initiate SIFT detector
                sift = cv2.xfeatures2d.SIFT_create()

                # find the keypoints and descriptors with SIFT
                kp1, des1 = sift.detectAndCompute(oim,None)
                kp2, des2 = sift.detectAndCompute(nim,None)

                #print(str(len(kp1))+","+str(len(kp2)))
                # create BFMatcher object
                bf = cv2.BFMatcher()
                if len(kp1) > 0 and len(kp2) > 0:
                    # Match descriptors.
                    matches = bf.knnMatch(des2,des1, k=2)
                    #print(matches)
                    IDs.append(oldPostit.ID)
                    for m,n in matches:
                        #print(str(m.distance)+"<"+str(0.2*n.distance))
                        #print(m.distance <(0.2*n.distance))
                        #print(good)
                        if m.distance <(0.75*n.distance):
                            good[p] = good[p] + 1
                else:
                    #print("here")
                    img = self.getPrevCanvasImage()
                    cv2.imshow("thing",cv2.resize(img,None,fx=0.5,fy=0.5))
                    cv2.waitKey(0)
                    cv2.imshow("thing",oim)
                    cv2.waitKey(0)

            #print(good)
            try:
                if max(good)>10:
                    maxidx = np.argmax(good)
            except:
                pass

            # print(len(goodMatches))
            if (maxidx == -1):
                # Create new entry on list of active postits and then add ID to list
                newID = uuid.uuid4()
                createdPostit =  Postit(newID, newPostit["position"][0], newPostit["position"][1],
                                        newPostit["position"][2], newPostit["position"][3], newPostit["colour"],True,self.newID)
                newUniquePostits.append(createdPostit)
                postitIDs.append(newID)
                activePostitsFound.append(newID)
            else:
                # Return ID of Matched postits
                updatingPostit = self.activePostits.pop(maxidx)
                postitIDs.append(updatingPostit.getID())
                activePostitsFound.append(updatingPostit.getID())
                updatingPostit.update(newPostit,self.newID)
                self.activePostits.insert(maxidx,updatingPostit)

        for p, oldPostit in enumerate(self.activePostits):
            if oldPostit.ID not in activePostitsFound:
                oldPostit.setState(False)
        self.activePostits.extend(newUniquePostits)


        return postitIDs

    # Compare lines found with know list of connections
    def updateLines(self,postitIDs, lines):
        for cxn in lines:
            #print(cxn["postitIdx"][0])
            #print(len(postitIDs))
            connection = [postitIDs[cxn["postitIdx"][0]],postitIDs[cxn["postitIdx"][1]]]
            if connection not in self.postitConnections:
                self.postitConnections.append(connection)

    def imageSettings(self, mipa, mapa, lento, sig, mico, maco, poth):
        self.minPostitArea = mipa
        self.maxPostitArea = mapa
        self.lenTolerence = lento
        self.maxColourThresh = maco
        self.minColourThresh = mico
        self.postitThresh = poth
        self.sigma = sig

    def setDebug(self, state):
        self.debug = state

    def bwSmooth(self, image):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        grayImg = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        normImg = clahe.apply(grayImg)
        smoothImg = cv2.bilateralFilter(normImg,9,75,75)
        return smoothImg

    # Main update loop using the current settings to extract data from current rawImage
    def update(self):
        canvasImage = self.getCanvasImage()
        extractor = GraphExtractor(canvasImage)
        graph = extractor.extractGraph(self.debug, self.minPostitArea,self.maxPostitArea, self.lenTolerence,
                                       self.minColourThresh, self.maxColourThresh, self.postitThresh)
        self.newID = uuid.uuid4()
        self.comparePrev(graph)

        newCanvas = Canvas(self.newID, self.snapshotTime,self.rawImage,self.canvasBounds,self.activePostits,self.postitConnections,self.prevCanvasID)
        self.canvasConnections.append([self.prevCanvasID, self.newID])
        self.prevCanvasID = self.newID
        self.canvasList.append(newCanvas)

    # For testing construct the current canvas into a visual display for projecting back on to physical postits
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
                    for canvas in self.canvasList:
                        if canvas.ID == postit.last_canvas_ID:
                            postitImage = postit.getImage(canvas.getImage(self.rawImage))
                            dispImage[y1:y1+postitImage.shape[0], x1:x1+postitImage.shape[1]] = postitImage
                            cv2.rectangle(dispImage,(x1,y1),(x2,y2),(0,200,200),thickness=4)

            r = 720 / dispImage.shape[1]
            dim = (720, int(dispImage.shape[0] * r))

            # perform the actual resizing of the image and show it
            dispImage = cv2.resize(dispImage, dim, interpolation = cv2.INTER_AREA)
            cv2.imshow("Display", dispImage)
            cv2.waitKey(0)

if __name__ == "__main__":

    ######
    # When Using this test code follow these steps to minimize problems with image processing
    # 1.    Set background of projector to white
    # 2.    Run this script
    # 3.    Add initial postits
    # 4.    Cover the projector and pess enter with the console selected
    # 5.    Drag the "Display" window to be shown on projector, and uncover projector. Do not close this window
    # 6.    Make changes to postit layout
    # 7.    Cover the projector and pess enter, this time with the "Display" window selected
    # 8.    Uncover projector
    # 9.    If expected postits are missing
    #           goto Deubug.
    # 10.   Else goto 6.
    #
    # Debug:
    #   - Area being cropped out as the canvas is not correct
    #       ~ Cause : Brightness in the room differs from test conditions
    #       ~ Fix   : Change find canvas threshold
    #   - Postit not found
    #       ~ Cause : Brightness in the room differs from test conditions
    #       ~ Fix   : Change find postit threshold
    ######
    # boardModel = Model()
    # r = requests.get("http://localhost:8080") # Request image from phone
    # # Receiving an image from the request gives code 200, all other returns means that the image has no been obtained
    # if r.status_code == 200:
    #     print("Got Good Calibartion Image")
    #     nparray = np.asarray(bytearray(r.content), dtype="uint8") # Transform byte array to numpy array
    #     canvImg = cv2.imdecode(nparray,cv2.IMREAD_COLOR) # Decode values as openCV colours
    #     boardModel.newCalibImage(canvImg) #set as calibration image
    #     boardModel.runAutoCalibrate() # Autocalibratefrom image
    # else:
    #     print(":( Got Bad Calibration Image")
    #     print(r.text)
    # input("Waiting >")
    # while(1):
    #     r = requests.get("http://localhost:8080")
    #     if r.status_code == 200:
    #         print("Got Good Postit Image")
    #         nparray = np.asarray(bytearray(r.content), dtype="uint8")
    #         img = cv2.imdecode(nparray,cv2.IMREAD_COLOR)
    #         boardModel.newRawImage(img, datetime.datetime.now(),update=1)
    #         boardModel.display()
    #     else:
    #         print(":( Got Bad Postit Image")
    #         print(r.text)


    canvImg = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154758.jpg')
    boardModel = Model()
    boardModel.setDebug(False)
    boardModel.newCalibImage(canvImg)
    boardModel.runAutoCalibrate(showDebug = True)
    boardModel.imageSettings(5000,50000,0.4,0.33,64,200,120)
    image1 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154813.jpg')
    boardModel.newRawImage(image1, datetime.datetime.now(), 1)
    print("1")
    boardModel.display()
    image2 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154821.jpg')
    boardModel.newRawImage(image2, datetime.datetime.now(),1)
    print("2")
    boardModel.display()
    image3 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154813b.jpg')
    boardModel.newRawImage(image3, datetime.datetime.now(),1)
    print("3")
    boardModel.display()
    image4 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154813c.jpg')
    boardModel.newRawImage(image4, datetime.datetime.now(),1)
    print("4")
    boardModel.display()
    image5 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154813d.jpg')
    boardModel.newRawImage(image5, datetime.datetime.now(),1)
    print("5")
    boardModel.display()

    #boardModel.save("canvas_data")
    #newBoard = Model()
    #newBoard.load("canvas_data")
    #newBoard.display()


