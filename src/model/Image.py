import datetime
import uuid
import PIL
import io
import base64
import cv2
import os
import requests
import numpy
from SqliteObject import SqliteObject
from src.model.User import User


class Image(SqliteObject):

    properties = ["id", "user", "timestamp"]
    table = "images"

    def __init__(self, user, npArray=None, id=uuid.uuid4(), timestamp=datetime.datetime.now(), database=None):
        super().__init__(id=id,
                         database=database)
        self.user = user
        self.image = npArray
        self.timestamp = timestamp

    @staticmethod
    def from_uri(user, uri='http://localhost:8080'):
        response = requests.get(uri)

        if response.status_code == 200:
            nparray = numpy.asarray(bytearray(requests.content), dtype="uint8")
            return Image(user=user,
                         npArray=cv2.imdecode(nparray, cv2.IMREAD_COLOR))
        else:
            print(response.status_code)
            print(response.json())
            return None

    def image_as_base64(self):
        img = PIL.Image.fromarray(self.image)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
        # $('div').css('background-image', 'url(data:image/gif;base64,' + a.image + ')');

    def get_user(self):
        if type(self.user) == int:
            return User.get(id=id)

        return self.user

    def get_user_id(self):
        if type(self.user) == int:
            return self.user
        else:
            return self.user.get_id()

    def get_image(self):
        if not self.image:
            self.image = cv2.imread(self.get_path())

        return self.image

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def create(self, database=None):
        super(Image, self).create(database=database)
        cv2.imwrite(self.get_path(), self.image)
        return self

    def delete(self, database=None):
        super(Image, self).delete(database=database)
        os.remove(self.get_path())

    def get_path(self):
        return Image.get_image_path(self.id)

    @staticmethod
    def get_image_path(id):
        base_path = os.path.join(os.getcwd(), './server/static/images')
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        path = os.path.join(base_path, str(id) + ".jpg")
        return path
