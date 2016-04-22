from flask import render_template, send_from_directory
from src.server import (app, socketio)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/canvas')
def canvas():
    return render_template('canvas.html')

@app.route('/hud')
def hud():
    return render_template('hud.html')

@app.route('/debug')
def debug():
    return render_template('debug.html')

@app.route('/js/<path:path>')
def js_serve(path):
    print(path)
    return send_from_directory('static/js', path)

@app.route('/styles/<path:path>')
def css_serve(path):
    print(path)
    return send_from_directory('static/styles', path)
