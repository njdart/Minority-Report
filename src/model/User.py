from src.model.SqliteObject import SqliteObject


class User(SqliteObject):

    properties = ["id", "username"]
    table = "users"

    def __init__(self, username, id=None, database=None):
        super().__init__(id=id, database=database)
        self.username = username

    def set_username(self, username):
        self.username = username
        return self

    def get_username(self):
        return self.username

    def get_id(self):
        return self.id

    def as_object(self):
        return {
            "username": self.username,
            "id": self.id
        }
