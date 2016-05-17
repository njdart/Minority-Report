import uuid
from src.model.SqliteObject import SqliteObject


class User(SqliteObject):
    properties = [
        "id",
        "name"
    ]

    table = "users"

    def __init__(self,
                 name="New User",
                 id=uuid.uuid4(),):
        super(User, self).__init__(id=id)

        self.name = name