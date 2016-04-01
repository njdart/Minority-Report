class Canvas:
    """A snapshot of the state of the canvas and the inerpretation of it"""
    def __init__(self, newid, time, boardImage, canvasBounds, postits, cxns, prevCanvID):
        self.ID = newid
        self.timestamp = time
        self.rawImage = boardImage
        self.bounds = canvasBounds
        self.postits = postits
        self.connections = cxns
        self.derivedFrom = prevCanvID

    def getPostit(self,ID):
        for postit in self.postits:
            if postit.ID == ID:
                return postit
        return None

    def getImage(self,boardImage):
        canvasStartX = self.bounds[0]
        canvasStartY = self.bounds[1]
        canvasEndX = self.bounds[0]+self.bounds[2]
        canvasEndY = self.bounds[1]+self.bounds[3]
        return self.rawImage[canvasStartY:canvasEndY, canvasStartX:canvasEndX]



    def getUUID(self):
        return self.ID



if __name__ == "__main__":
    pass