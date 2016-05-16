from flask_socketio import emit
from src.server import socketio
import json
import base64
from PIL import Image
import io

@socketio.on("getKinectImage")
def getKinectImage(data):
    bmpData = base64.b64decode(data["b64Bitmap"])
    stream = io.BytesIO(bmpData)
    image = Image.open(stream)
    print(image.size)
