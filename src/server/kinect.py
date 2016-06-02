from flask import request
from flask.json import jsonify
from src.model import (GetKinectEnable, ToggleKinectEnable)
from src.model.Image import Image
from src.model.InstanceConfiguration import InstanceConfiguration
from src.model.Session import Session
from src.server import (app, socketio)
from src.server.api.image_api import generate_canvas
import time
import uuid

@app.route('/boardObscured', methods=['GET', 'POST'])
def boardObscured():
    if request.method == "GET":
        return "404 pls post instead kek", 404

    print("/boardObscured, POST")
    print(request.data)

    if request.get_json()["boardObscured"]:
        print("board obscured")
        socketio.emit("body_detected", broadcast=True)
        return jsonify({"message": "nothing to do"}), 200

    print("board not obscured")
    socketio.emit("body_not_detected", broadcast=True)
    # ignore message if global flag is set
    if not GetKinectEnable():
        print("ignoring (kinectEnable = False)")
        return jsonify({"message": "echo that. ignoring due to kinectEnable flag."}), 200

    # IP address 127.0.0.1 is localhost
    localhosts = ["127.0.0.1", "localhost", "::1"]
    kinectHost = request.remote_addr
    if kinectHost in localhosts:
        kinectHost = "localhost"

    # get instance config
    config = InstanceConfiguration.get_config_by_kinect(kinectHost)
    if config is None:
        print("kinect's IP matches no instance configurations")
        return jsonify({"message": "your IP does not belong to any instance configurations."}), 400

    # blank canvas
    socketio.emit("blank_canvas_black", config.id, broadcast=True)
    time.sleep(0.5)

    # take picture
    id = config.get_camera_image()
    if id is None:
        return jsonify({"message": "failed to take photo."}), 500

    # generate canvas from picture
    image = Image.get(id=id)
    current_canvas = Session.get(InstanceConfiguration.get(id=image.instanceConfigurationId).sessionId).get_latest_canvas()
    next_canvas_id = uuid.uuid4()
    postits, old_to_new_postits = image.find_postits(next_canvas_id=next_canvas_id,
                                 current_canvas=current_canvas,
                                 save=True)
    connections = image.find_connections(postits=postits,
                                         old_to_new_postits=old_to_new_postits,
                                         current_canvas=current_canvas,
                                         next_canvas_id=next_canvas_id,
                                         save=True)
    canvases = image.update_canvases(new_postits=postits,
                                     connections=connections,
                                     current_canvas=current_canvas,
                                     next_canvas_id=next_canvas_id)

    print("Automatic canvas generation succeeded.")
    socketio.emit('create_canvas', [canvas.as_object() for canvas in canvases])
    return jsonify({"message": "generated canvas from new image."}), 200