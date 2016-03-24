class Canvas:
    """A snapshot of the state of the canvas and the inerpretation of it"""
    def __init__(self, newid, time, boardImage, canvasBounds, postits, cxns):
        self.ID = newid
        self.timestamp = time
        self.rawImage = boardImage
        self.bounds = canvasBounds
        self.postits = postits
        self.connections = cxns

    def getPostit(self,ID):
        for postit in self.postits:
            if postit.ID == ID:
                return postit
        return None



    def getUUID(self):
        return self.ID



if __name__ == "__main__":
    pass