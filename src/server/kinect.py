from src.server import app
from flask import request
from flask.json import jsonify
from src.model.InstanceConfiguration import InstanceConfiguration
from src.server.api.image_api import generate_canvas
from src.model.Image import Image
import uuid
from src.model.Session import Session
from src.server import (app, socketio)

@app.route('/boardObscured', methods=['GET', 'POST'])
def boardObscured():
    if request.method == "GET":
        return "404 pls post instead kek", 404

    print("/boardObscured, POST")
    print(request.data)

    if request.get_json()["boardObscured"]:
        print("board not obscured")
        return jsonify({"message": "nothing to do"}), 200

    print("board obscured")

    # take picture if not obscured
    config = InstanceConfiguration.get_config_by_kinect(request.remote_addr)
    if config is None:
        print("kinect's IP matches no instance configurations")
        return jsonify({"message": "your IP does not belong to any instance configurations."}), 400

    id = config.get_camera_image()
    if id is None:
        return jsonify({"message": "failed to take photo."}), 500


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