from flask.ext.socketio import emit
from src.server import socketio
from src.model.Users import User
import uuid


@socketio.on('create_user')
def create_user(username):
    """
    Create a user
    :param username: string Username
    :return: user object eg:
    {
        "username": "fooname",
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    }
    """
    emit('create_user', User(name=username).create().as_object())


@socketio.on('get_users')
def get_users():
    """
    Get a list of all users
    :return: list of all users eg:
    [
        {
            "username": "fooname",
            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        },
        ...
    ]
    """
    emit('get_users', [user.as_object() for user in User.get_all()])


@socketio.on('update_user')
def update_user(id, username):
    """
    Update a user given an id
    :param id: string UUID of a user
    :param username: string username to change the user's name to
    :return: the new users details eg:
    {
        "username": "fooname",
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    }
    """
    user = User.get(id=id)
    user.name = username
    emit('update_user', user.update().as_object())


@socketio.on('delete_user')
def delete_user(id):
    """
    Delete a user
    :param id: string the UUID of the user to delete
    :return: True if the user was deleted, False otherwise
    """
    emit('delete_user', User.get(id=id).delete())


print('Registered Users API methods')
