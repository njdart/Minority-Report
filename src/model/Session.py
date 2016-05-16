import uuid
from src.model.SqliteObject import SqliteObject


class Session(SqliteObject):
    properties = [
        "id",
        "name",
        "description"
    ]

    table = "session"

    def __init__(self,
                 name=None,
                 description = None,
                 id=uuid.uuid4(),):
        super(Session, self).__init__(id=id)

        self.name = name or "A Whiteboard Story"
        self.description = description or "Snowboard and the 7 postits"
