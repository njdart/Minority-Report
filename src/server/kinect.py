from src.server import app
from flask import request
from flask.json import jsonify
from src.model.InstanceConfiguration import InstanceConfiguration
from src.server.api.image_api import generate_canvas

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

    generate_canvas(id)
    print("Automatic canvas generation succeeded.")
    return jsonify({"message": "generated canvas from new image."}), 200