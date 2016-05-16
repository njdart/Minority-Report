from flask.ext.socketio import emit
from src.server import socketio
from src.model.Session import Session


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

print('Registered Session API methods')
