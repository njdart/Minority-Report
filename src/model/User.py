from src.model.SqliteObject import SqliteObject


class User(SqliteObject):

    def __init__(self, username, id=None, databaseHandler=None):
        super().__init__(properties=["id", "username"], table="users", databaseHandler=databaseHandler)
        self.username = username
        self.id = id

    @staticmethod
    def from_database_tuple(tuple, databaseHandler=None):

        if not tuple:
            return None
        return User(id=tuple[0], username=tuple[1], databaseHandler=databaseHandler)

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
