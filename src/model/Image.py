import datetime
import uuid
import PIL
import io
import base64
import cv2
import os
from src.model.SqliteObject import SqliteObject


class Image(SqliteObject):

    def __init__(self, user, npArray, id=None, timestamp=None, databaseHandler=None):
        super().__init__(properties=["id", "user", "timestamp"], table="images", databaseHandler=databaseHandler)
        self.user = user
        self.image = npArray.copy()
        self.id = id if id is not None else uuid.uuid4()
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now()

    @staticmethod
    def from_database_tuple(tuple, databaseHandler=None):
        if not tuple:
            return None

        print(tuple[2])

        return Image(id=uuid.UUID(tuple[0]),
                     user=databaseHandler.get_user(id=tuple[1]),
                     timestamp=datetime.datetime.strptime(tuple[2], '%Y-%m-%d %H:%M:%S.%f'),
                     databaseHandler=databaseHandler,
                     npArray=cv2.imread(Image.get_image_path(tuple[0])))

    def image_as_base64(self):
        img = PIL.Image.fromarray(self.image)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
        # $('div').css('background-image', 'url(data:image/gif;base64,' + a.image + ')');

    def as_object(self):
        return {
            "user": self.get_user_id(),
            "id": str(self.id),
            "timestamp": self.timestamp.isoformat()
        }

    def get_user(self):
        if type(self.user) == int:
            if self.databaseHandler:
                self.user = self.databaseHandler.get_user(id=self.user)
            else:
                raise Exception('No Database Handler available to look up user')

        return self.user

    def get_user_id(self):
        if type(self.user) == int:
            return self.user
        else:
            return self.user.get_id()

    def create(self, databaseHandler=None):
        SqliteObject.create(self, databaseHandler=databaseHandler)
        cv2.imwrite(self.get_path(), self.image)
        return self

    def get_path(self):
        return Image.get_image_path(self.id)

    @staticmethod
    def get_image_path(id):
        base_path = os.path.join(os.getcwd(), './model/images/')
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        path = os.path.join(base_path, str(id) + ".jpg")
        return path
