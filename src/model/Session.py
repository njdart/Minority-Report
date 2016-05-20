import uuid
from src.model.SqliteObject import SqliteObject
from src.server import databaseHandler


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

    def get_latest_canvas(self):
        from src.model.Canvas import Canvas

        if self.database:
            c = self.database.cursor()
        else:
            c = databaseHandler().get_database().cursor()

        query = 'SELECT (id) FROM canvases WHERE session="{}" ORDER BY datetime(derivedAt) DESC LIMIT 1;'.format(self.id)

        c.execute(query)
        data = c.fetchone()

        if data is None:
            return None

        return Canvas.get(data[0])

    def create_new_canvas(self):
        from src.model.Canvas import Canvas

        canvas = self.get_latest_canvas()
        if canvas is None:
            return Canvas(session=self.id)

        return canvas.clone()
