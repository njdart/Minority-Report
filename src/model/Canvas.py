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
        pass



    def getUUID(self):
        return self.ID



if __name__ == "__main__":
    pass