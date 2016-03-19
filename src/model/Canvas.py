from datetime import datetime


class Canvas:
    """
    Represents a snapshot of a canvas (image with postits and whiteboard)
    """

    def __init__(self, image=None, bounds=None, transformation=None, canvas=None):
        """
        Construct a canvas from an image, bounds and transformation matric (or an existing canvas represented as an
        object, see docs/storage.md
        :param image:
        :param bounds:
        :param transformation:
        :param canvas:
        :return:
        """

        self.ID
        self.rawImage
        self.bounds
        self.timestamp = datetime.now()

    def getPostit(self, ID):
        pass

    def getUUID(self):
        return self.ID

    def getTimestamp(self):
        return self.createdTimestamp

if __name__ == "__main__":
    pass
