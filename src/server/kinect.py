from server import app

@app.route("/kinect/body")
def body_data():
    return "body data page"

@app.route("/kinect/gesture")
def gesture_data():
    return "gesture data page"
