import datetime
import uuid
from src.model.SqliteObject import SqliteObject
import cv2
import os


class Image(SqliteObject):

    def __init__(self, user, npArray, id=None, timestamp=None, databaseHandler=None):
        super().__init__(properties=["id", "user", "timestamp"], table="users", databaseHandler=databaseHandler)
        self.user = user
        self.image = npArray.copy()
        self.id = id if id is not None else uuid.uuid4()
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now()

    @staticmethod
    def from_database_tuple(tuple, databaseHandler=None):
        if not tuple:
            return None

        return Image(id=tuple[0],
                     user=databaseHandler.get_user(tuple[1]),
                     timestamp=tuple[2],
                     databaseHandler=databaseHandler,
                     npArray=cv2.imread(os.path.join(Image.getPath(), str(tuple[0])+".jpg")))

    def as_object(self):
        return {
            "user": self.user.id(),
            "id": self.id,
            "timestamp": self.timestamp
        }

    @staticmethod
    def getPath():
        path = os.path.join(os.getcwd(), '/model/images/')
        os.makedirs(path)
        return path

    def getImagePath(self):
        return os.path.join(self.getPath, str(self.id)+".jpg")
