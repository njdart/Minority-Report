from flask.ext.socketio import emit
from src.server import socketio
from src.model.Session import Session
from src.model.Canvas import Canvas
from src.model.Postit import Postit
from src.model.Connection import Connection
import uuid
import pdb


@socketio.on('create_session')
def create_session(name, description):
    """
    Create a session for users to join into
    :param name: string the session name
    :param description: string a brief description of the session
    :return: a session object eg:
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "name": "fooName",
        "description": "fooDescription in short form"
    }
    """
    emit('create_session', Session(name=name, description=description).create().as_object())


@socketio.on('get_sessions')
def get_sessions():
    """
    Get a list of all sessions a user can join
    :return: a list of sessions eg:
    [
        {
            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "name": "fooName",
            "description": "fooDescription in short form"
        },
        ...
    ]
    """
    emit('get_sessions', [session.as_object() for session in Session.get_all()])


@socketio.on('update_session')
def update_session(id, name, description):
    """
    Update an existing session
    :param id: string the session id
    :param name: the new name of the session
    :param description: the new description of the session
    :return: the updated description eg:
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "name": "fooName",
        "description": "fooDescription in short form"
    }
    """
    session = Session.get(id=id)
    session.name = name
    session.description = description
    emit('update_session', session.update().as_object())


@socketio.on('delete_session')
def delete_session(id):
    """
    Delete an existing session
    :param id: string the id of the session
    :return: True if the session was deleted, False otherwise
    """
    emit('delete_session', Session.get(id=id).delete())



@socketio.on('get_postits_by_session')
def get_postits_by_session(sessionId):
    session = Session.get(sessionId)
    if session is not None:
        canvases = Canvas.get_by_property(sessionId, prop="session")
        postits = []
        print("canvases {}".format(canvases))
        pdb.set_trace()
        for canvas in canvases:
            postits.extend(Postit.get_by_property(canvas.id, prop="canvas"))
        print("Postits {}".format(postits))
        postits = list(set([postit.as_object() for postit in postits]))
        emit('get_postits_by_session', postits)
    else:
        emit('get_postits_by_session', None)


@socketio.on('get_latest_canvas_by_session')
def get_latest_canvas_by_session(sessionId):
    session = Session.get(sessionId)
    if session is not None:
        canvas = Canvas.get_latest_canvas_by_session(sessionId)
        if (canvas is not None):
            postits = Postit.get_by_property("canvas", canvas.id)
            connections = Connection.get_by_property("canvas", canvas.id)
            print("canvas {}".format(canvas))
            print("Postits {}".format(postits))

            data = {
                "canvas":      canvas.as_object(),
                "postits":     [postit.as_object() for postit in postits],
                "connections": [connection.as_object() for connection in connections]
            }
            emit('get_latest_canvas_by_session', data)
    else:
        emit('get_latest_canvas_by_session', None)


@socketio.on("purge_sessions")
def purge_sessions():
    for s in Session.get_all():
        s.delete()


print('Registered Session API methods')
