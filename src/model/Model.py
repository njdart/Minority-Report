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

        self.simpleBounds = []
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
            if canvas.get_id() == ID:
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
        self.simpleBounds = cv2.boundingRect(canvasContour)

        fCanvasContours = canvasContour.flatten()
        canvX = np.zeros([int(len(fCanvasContours)/2),1])
        canvY = np.zeros([int(len(fCanvasContours)/2),1])
        l1 = np.zeros(int(len(fCanvasContours)/2))
        l2 = np.zeros(int(len(fCanvasContours)/2))
        l3 = np.zeros(int(len(fCanvasContours)/2))
        l4 = np.zeros(int(len(fCanvasContours)/2))
        for i in range(0,len(fCanvasContours),2):
            canvX[int(i/2)] =  fCanvasContours[i]
            canvY[int(i/2)] =  fCanvasContours[i+1]
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
        canvasPts = [(canvX[max1][0], canvY[max1][0]), (canvX[max2][0], canvY[max2][0]), (canvX[max3][0], canvY[max3][0]), (canvX[max4][0], canvY[max4][0])]

        if showDebug:
            debugImage = image.copy()
            for c in boardContours:
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(debugImage,boardContours,max_index,(0,0,255),2)
                cv2.circle(debugImage,(canvX[max1],canvY[max1]),4,(0,255,0), thickness=5)
                cv2.circle(debugImage,(canvX[max2],canvY[max2]),4,(0,255,0), thickness=5)
                cv2.circle(debugImage,(canvX[max3],canvY[max3]),4,(0,255,0), thickness=5)
                cv2.circle(debugImage,(canvX[max4],canvY[max4]),4,(0,255,0), thickness=5)
            cv2.imshow("debug",cv2.resize(debugImage,None,fx=0.25,fy=0.25))
            #cv2.imshow("debug",debugImage)
            cv2.waitKey(0)

        return np.array(canvasPts)

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

    # Using canvasBounds on rawImage extract an image of the canvas
    def getCanvasImage(self):
        #canvasStartX = self.canvasBounds[0]
        #canvasStartY = self.canvasBounds[1]
        #canvasEndX = self.canvasBounds[0]+self.canvasBounds[2]
        #canvasEndY = self.canvasBounds[1]+self.canvasBounds[3]
        #return self.rawImage[canvasStartY:canvasEndY, canvasStartX:canvasEndX]
        return self.four_point_transform(self.rawImage,self.canvasBounds)

    def getPrevCanvasImage(self, ID):
        if ID == self.newID:
            return self.getCanvasImage()
        else:
            canvas = self.getCanvas(ID)
            return self.four_point_transform(canvas.image, self.canvasBounds)

    # Compare current graph with previous graph
    def comparePrev(self,newGraph):
        postitIDs = self.updatePostits(newGraph["postits"])
        self.updateLines(postitIDs,newGraph["lines"])

    # Compare a new list of postits to the list of known active postits
    def updatePostits(self,newPostits):
        postitIDs = []
        activePostitsFound = []
        newUniquePostits = []
        for o,newPostit in enumerate(newPostits):
            maxidx = -1
            good = np.zeros(len(self.activePostits), dtype=np.int)
            #print(len(self.activePostits))
            IDs = []
            for p, oldPostit in enumerate(self.activePostits):
                oim = self.bwSmooth(oldPostit.get_postit_image(self.getPrevCanvasImage(oldPostit.get_canvas())))
                nim = self.bwSmooth(newPostit["image"])
                #cv2.imshow("nimR",oldPostit.getImage(self.getPrevCanvasImage(oldPostit.last_canvas_ID)))
                #cv2.imshow("nim",nim)
                #cv2.imshow("oimR",newPostit["image"])
                #cv2.imshow("oim",oim)
                #cv2.waitKey(0)
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
                    IDs.append(oldPostit.get_id())
                    for m,n in matches:
                        #print(str(m.distance)+"<"+str(0.2*n.distance))
                        #print(m.distance <(0.2*n.distance))
                        #print(good)
                        if m.distance <(0.75*n.distance):
                            good[p] = good[p] + 1
                else:
                    #print("here")
                    cv2.imshow("thing",oim)
                    cv2.waitKey(0)

            print(good)
            try:
                if max(good)>10:
                    maxidx = np.argmax(good)
            except:
                pass

            # print(len(goodMatches))
            if (maxidx == -1):
                # Create new entry on list of active postits and then add ID to list
                newID = uuid.uuid4()
                createdPostit =  Postit(x=newPostit["position"][0],
                                        y=newPostit["position"][1],
                                        width=newPostit["position"][2],
                                        height=newPostit["position"][3],
                                        pnt1X=newPostit["points"][0][0],
                                        pnt1Y=newPostit["points"][0][1],
                                        pnt2X=newPostit["points"][1][0],
                                        pnt2Y=newPostit["points"][1][1],
                                        pnt3X=newPostit["points"][2][0],
                                        pnt3Y=newPostit["points"][2][1],
                                        pnt4X=newPostit["points"][3][0],
                                        pnt4Y=newPostit["points"][3][1],
                                        colour=newPostit["colour"],
                                        id=newID,
                                        canvas=self.newID
                                        )
                newUniquePostits.append(createdPostit)
                postitIDs.append(newID)
                activePostitsFound.append(newID)
            else:
                # Return ID of Matched postits
                updatingPostit = self.activePostits.pop(maxidx)
                postitIDs.append(updatingPostit.get_id())
                activePostitsFound.append(updatingPostit.get_id())
                updatingPostit.update_postit(x=newPostit["position"][0],
                                        y=newPostit["position"][1],
                                        width=newPostit["position"][2],
                                        height=newPostit["position"][3],
                                        pnt1X=newPostit["points"][0][0],
                                        pnt1Y=newPostit["points"][0][1],
                                        pnt2X=newPostit["points"][1][0],
                                        pnt2Y=newPostit["points"][1][1],
                                        pnt3X=newPostit["points"][2][0],
                                        pnt3Y=newPostit["points"][2][1],
                                        pnt4X=newPostit["points"][3][0],
                                        pnt4Y=newPostit["points"][3][1],
                                        colour=newPostit["colour"],
                                        canvas=self.newID,
                                        physical=True
                                        )
                self.activePostits.insert(maxidx,updatingPostit)

        for p, oldPostit in enumerate(self.activePostits):
            if oldPostit.get_id() not in activePostitsFound:
                oldPostit.set_physical(False)
        self.activePostits.extend(newUniquePostits)


        return postitIDs

    # Compare lines found with know list of connections
    def updateLines(self,postitIDs, lines):
        for cxn in lines:
            #print(cxn)
            #print(cxn["postitIdx"][0])
            #print(len(postitIDs))
            if "postitIdStart" in cxn.keys():
                start = cxn["postitIdStart"]
            else:
                start = postitIDs[cxn["postitIdx"][0]]
            if "postitIdEnd" in cxn.keys():
                end = cxn["postitIdEnd"]
            else:
                end = postitIDs[cxn["postitIdx"][1]]
            connection = [start,end]
            #print(connection)
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
        smoothImg = cv2.bilateralFilter(normImg,3,75,75)
        return smoothImg

    # Main update loop using the current settings to extract data from current rawImage
    def update(self):
        canvasImage = self.getCanvasImage()
        extractor = GraphExtractor(canvasImage, self.activePostits)
        graph = extractor.extractGraph(self.debug, self.minPostitArea,self.maxPostitArea, self.lenTolerence,
                                       self.minColourThresh, self.maxColourThresh, self.postitThresh)
        self.newID = uuid.uuid4()
        self.comparePrev(graph)
        newCanvas = Canvas(image=self.rawImage,
                           canvasBounds=self.canvasBounds,
                           id=self.newID,
                           postits=self.activePostits,
                           connections=self.postitConnections,
                           derivedFrom=self.prevCanvasID,
                           derivedAt=self.snapshotTime
                           )
        self.canvasConnections.append([self.prevCanvasID, self.newID])
        self.prevCanvasID = self.newID
        self.canvasList.append(newCanvas)

    # For testing construct the current canvas into a visual display for projecting back on to physical postits
    def display(self):
        if len(self.canvasList):
            lastCanvas = self.canvasList[-1]
            dispImage = np.zeros((self.simpleBounds[3], self.simpleBounds[2], 3), np.uint8)
            for line in lastCanvas.connections:
                startPoint = (int(lastCanvas.get_postit(line[0]).get_position()[0]+(lastCanvas.get_postit(line[0]).get_size()[0])/2),
                              int(lastCanvas.get_postit(line[0]).get_position()[1]+(lastCanvas.get_postit(line[0]).get_size()[1])/2))
                endPoint = (int(lastCanvas.get_postit(line[1]).get_position()[0]+(lastCanvas.get_postit(line[1]).get_size()[0])/2),
                            int(lastCanvas.get_postit(line[1]).get_position()[1]+(lastCanvas.get_postit(line[1]).get_size()[1])/2))
                cv2.line(dispImage, startPoint, endPoint, [255,0,0], thickness=4)
            for postit in lastCanvas.postits:
                for canvas in self.canvasList:
                    if canvas.get_id() == postit.get_canvas():
                        postitImage = postit.get_postit_image(self.four_point_transform(canvas.image, self.canvasBounds))
                x1 = postit.get_position()[0]
                y1 = postit.get_position()[1]
                x2 = postit.get_position()[0]+postit.get_size()[0]
                y2 = postit.get_position()[1]+postit.get_size()[1]
                if postit.physical == 1:
                    cv2.rectangle(dispImage,(x1,y1),(x2,y2),(0,0,0),thickness=cv2.FILLED)
                    cv2.rectangle(dispImage,(x1,y1),(x2,y2),(0,255,0),thickness=4)
                elif postit.physical == 0:
                    cv2.rectangle(dispImage,
                                  (x1,y1),
                                  (x1+postitImage.shape[1],y1+postitImage.shape[0]),
                                  (0,0,0),
                                  thickness=cv2.FILLED)
                    dispImage[y1:y1+postitImage.shape[0], x1:x1+postitImage.shape[1]] = postitImage
                    cv2.rectangle(dispImage,
                                  (x1,y1),
                                  (x1+postitImage.shape[1],y1+postitImage.shape[0]),
                                  (0,200,200),
                                  thickness=4)

            r = 1920 / dispImage.shape[1]
            dim = (1920, int(dispImage.shape[0] * r))

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
    #####
    boardModel = Model()
    boardModel.setDebug(False)
    boardModel.imageSettings(2000,40000,0.4,0.33,64,200,105)
    #input("Waiting for focus >")
    #requests.get("http://localhost:8080/focus")
    input("Waiting for boarders>")
    r = requests.get("http://localhost:8080") # Request image from phone
    # Receiving an image from the request gives code 200, all other returns means that the image has no been obtained
    if r.status_code == 200:
        print("Got Good Calibartion Image")
        nparray = np.asarray(bytearray(r.content), dtype="uint8") # Transform byte array to numpy array
        canvImg = cv2.imdecode(nparray,cv2.IMREAD_COLOR) # Decode values as openCV colours
        boardModel.newCalibImage(canvImg) #set as calibration image
        boardModel.runAutoCalibrate() # Autocalibratefrom image
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
            boardModel.newRawImage(img, datetime.datetime.now(),update=1)
            boardModel.display()
        else:
            print(":( Got Bad Postit Image")
            print(r.text)

    #
    # canvImg = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154758.jpg')
    # boardModel = Model()
    # boardModel.setDebug(False)
    # boardModel.newCalibImage(canvImg)
    # boardModel.runAutoCalibrate(showDebug = False)
    # boardModel.imageSettings(9000,20000,0.4,0.33,64,200,120)
    # image1 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154813.jpg')
    # boardModel.newRawImage(image1, datetime.datetime.now(), 1)
    # print("1")
    # boardModel.display()
    # image2 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154821.jpg')
    # boardModel.newRawImage(image2, datetime.datetime.now(),1)
    # print("2")
    # boardModel.display()
    # image3 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154813b.jpg')
    # boardModel.newRawImage(image3, datetime.datetime.now(),1)
    # print("3")
    # boardModel.display()
    # image4 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154813c.jpg')
    # boardModel.newRawImage(image4, datetime.datetime.now(),1)
    # print("4")
    # boardModel.display()
    # image5 = cv2.imread('/home/jjs/projects/Minority-Report/src/IMG_20160304_154813d.jpg')
    # boardModel.newRawImage(image5, datetime.datetime.now(),1)
    # print("5")
    # boardModel.display()

    #boardModel.save("canvas_data")
    #newBoard = Model()
    #newBoard.load("canvas_data")
    #newBoard.display()


