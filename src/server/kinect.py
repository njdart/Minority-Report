from src.server import app
from flask import request

@app.route("/kinect/body", methods=["POST"])
def body_data_post():
    return "body data page...<br><br>" + str(request.data)

@app.route("/kinect/gesture", methods=["POST"])
def gesture_data_post():
    return "gesture data page...<br><br>" + str(request.data)
