from flask import request
from flask.json import jsonify
from src.model import (GetKinectEnable, ToggleKinectEnable)
from src.model.Image import Image
from src.model.InstanceConfiguration import InstanceConfiguration
from src.model.Session import Session
from src.server import (app, socketio)
from src.server.api.image_api import generate_canvas
from src.server.sticky_note_selection import StickyNoteSelector
import time
import uuid

selector = StickyNoteSelector()
def getInstanceConfigByKinectHost(host):
    localhosts = ["127.0.0.1", "localhost", "::1"]
    kinectHost = host
    if kinectHost in localhosts:
        kinectHost = "localhost"
    return InstanceConfiguration.get_config_by_kinect(kinectHost)

@app.route("/canvasDimensions", methods=["POST"])
def canvasDimensions():
    config = getInstanceConfigByKinectHost(request.remote_addr)
    data = request.get_json()
    if data:
        data["configID"] = config.id
        socketio.emit("physical_canvas_dimensions", data, broadcast=True)
        return "fabulous", 200
    else:
        return "invalid request", 500

@app.route("/magicalHandCircles", methods=["POST"])
def magicalHandCircle():
    global selector
    data = request.get_json()
    if data:
        config = getInstanceConfigByKinectHost(request.remote_addr)
        data["configID"] = config.id
        socketio.emit("draw_circle", data, broadcast=True)
        hands = []
        for state in data["handStates"]:
            if state["leftHandTracked"]:
                hand = {"id":str(state["skeletonID"])+"L",
                        "closed":state["leftFistClosed"],
                        "posX":state["leftHandX"],
                        "posY":state["leftHandY"]}
                hands.append(hand)
            if state["rightHandTracked"]:
                hand = {"id":str(state["skeletonID"])+"R",
                        "closed":state["rightFistClosed"],
                        "posX":state["rightHandX"],
                        "posY":state["rightHandY"]}
                hands.append(hand)
        selector.update(hands)
        return "yay", 200
    else:
        return "invalid request", 500


@app.route('/boardObscured', methods=['GET', 'POST'])
def boardObscured():
    global selector
    if request.method == "GET":
        return "404 pls post instead kek", 404

    config = getInstanceConfigByKinectHost(request.remote_addr)

    print("/boardObscured, POST")
    print(request.data)

    if request.get_json()["boardObscured"]:
        print("board obscured")

        socketio.emit("body_detected", config.id, broadcast=True)
        return jsonify({"message": "nothing to do"}), 200

    print("board not obscured")
    socketio.emit("body_not_detected", config.id, broadcast=True)
    # ignore message if global flag is set
    if not GetKinectEnable():
        print("ignoring (kinectEnable = False)")
        return jsonify({"message": "echo that. ignoring due to kinectEnable flag."}), 200

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
    if image is None:
        return
    socketio.emit('show_loading')
    current_canvas = Session.get(InstanceConfiguration.get(id=image.instanceConfigurationId).sessionId).get_latest_canvas()
    next_canvas_id = uuid.uuid4()
    stickyNotes, old_to_new_stickyNotes = image.find_stickyNotes(next_canvas_id=next_canvas_id,
                                 current_canvas=current_canvas,
                                 save=True)
    selector.updateNotes(stickyNotes)
    connections = image.find_connections(stickyNotes=stickyNotes,
                                         old_to_new_stickyNotes=old_to_new_stickyNotes,
                                         current_canvas=current_canvas,
                                         next_canvas_id=next_canvas_id,
                                         save=True)
    canvases = image.update_canvases(new_stickyNotes=stickyNotes,
                                     connections=connections,
                                     current_canvas=current_canvas,
                                     next_canvas_id=next_canvas_id)

    print("Automatic canvas generation succeeded.")
    socketio.emit('create_canvas', [canvas.as_object() for canvas in canvases])
    return jsonify({"message": "generated canvas from new image."}), 200