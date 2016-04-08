import os
import sqlite3

from src.model.User import User


class ModelDatabase(object):
    """
    Handler and wrapper for the SQLite database used to store users and information about canvases and
    extracted postits
    """

    def __init__(self, file='./database.sqlite'):
        """
        Construct the database, applying the schema in schema.sql, to the desired database name
        """
        self.database = sqlite3.connect(file)

        with open(os.path.join(os.getcwd(), './model/schema.sql')) as schema:
            self.database.executescript(schema.read())

    def create_user(self, username):
        """
        Insert the user in to the database
        :argument username the username as a string
        :return True if the user was added, False otherwise
        """
        if not self.database:
            return False

        if not username:
            return False

        if not self.get_user(username=username):
            c = self.database.cursor()
            c.execute('INSERT INTO users (username) VALUES (?)', (username, ))
            self.database.commit()

            return self.get_user(username=username)

        return None

    def get_users(self):
        """
        Get all users from the database
        :return False if the database was not available, a list of (users, id) tuples otherwise
        """
        if not self.database:
            return False

        c = self.database.cursor()

        c.execute('SELECT * FROM users;')
        return [User.from_database_tuple(userTuple, databaseHandler=self) for userTuple in c.fetchall()]

    def get_user(self, username=None, id=None):
        """
        get a user from either their ID or their username
        :argument username the username as a string
        :argument id the id of the user
        :return the user row
        """
        if not username and not id:
            raise ValueError('Expected either a username or an id to look up a user')

        if not self.database:
            return False

        c = self.database.cursor()

        if username:
            c.execute('SELECT * FROM users WHERE username=?', (username, ))

        else:
            c.execute('SELECT * FROM users WHERE id=?', (id, ))

        return User.from_database_tuple(c.fetchone(), databaseHandler=self)

    def get_users_canvases(self, user):
        pass

    def get_canvas(self, canvasId):
        pass
