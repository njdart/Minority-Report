import datetime
import uuid
import PIL
import io
import base64
import cv2
import os
import requests
import numpy
from src.model.SqliteObject import SqliteObject
import pytz


class Image(SqliteObject):

    properties = ["id", "timestamp"]
    table = "images"

    def __init__(self,
                 npArray=None,
                 id=uuid.uuid4(),
                 timestamp=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC),
                 database=None):
        super().__init__(id=id,
                         database=database)
        self.image = npArray
        self.timestamp = timestamp

    @staticmethod
    def from_uri(user, uri='http://localhost:8080'):
        response = requests.get(uri)

        if response.status_code == 200:
            nparray = numpy.asarray(bytearray(response.content), dtype="uint8")
            return Image(id=uuid.uuid4(),
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

    def get_image(self):
        if not self.image:
            self.image = cv2.imread(self.get_image_path())

        return self.image

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def create(self, database=None):
        super(Image, self).create(database=database)
        cv2.imwrite(self.get_image_path(), self.image)
        return self

    def delete(self, database=None):
        super(Image, self).delete(database=database)
        os.remove(self.get_image_path())
        return self

    def get_image_path(self):
        return Image.get_image_directory(self.id)

    @staticmethod
    def get_image_directory(id):
        base_path = os.path.join(os.getcwd(), './server/static/images')
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        path = os.path.join(base_path, str(id) + ".jpg")
        return path

    @staticmethod
    def focus_camera(uri):
        uri += '/focus'
        print('Focusing Camera with URI ' + str(uri))
        response = requests.get(uri)
        print(response.status_code)
        return response.status_code == 200

    @staticmethod
    def get_camera_properties(uri):
        uri += "/properties"
        print('Getting Camera Properties from URI ' + str(uri))
        response = requests.get(uri)

        if response.status_code == 200:
            print('Got Good response from camera!')
            return response.json()
        else:
            print(response.status_code)
            print(response.json())
            return None

    @staticmethod
    def set_camera_properties(uri, properties):
        uri += "/properties"
        print('Setting Camera Properties with URI ' + str(uri))

        response = requests.post(uri, properties)

        print(response.status_code)

        return response.status_code == 200
