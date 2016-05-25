from src.model.SqliteObject import SqliteObject
from src.server import databaseHandler
import uuid
import datetime


class Canvas(SqliteObject):
    """
    A Canvas object relates to a session and contains a size of the canvas to be displayed
    """

    properties = [
        "id",
        "session",
        "derivedFrom",
        "derivedAt",
        "height",
        "width"
    ]

    table = "canvases"

    def __init__(self,
                 session,
                 id=uuid.uuid4(),
                 postits=[],
                 connections=[],
                 derivedFrom=None,
                 derivedAt=datetime.datetime.now(),
                 width=None,
                 height=None,
                 ):
        """
        :param session UUID v4 of session to which canvas belongs
        :param id UUID v4
        :param postits list of postit objects or UUID v4s
        :param connections list of (postit/postitUUID, postit/postitUUID) tuples
        :param derivedFrom canvas object or ID this object derives from
        :param width integer width of HUD
        :param height integer height of HUD
        """
        super(Canvas, self).__init__(id=id)
        self.session = session
        self.postits = postits
        self.connections = connections
        self.derivedFrom = derivedFrom
        self.derivedAt = derivedAt
        self.width = width if width is not None and height is not None else 1920
        self.height = height if width is not None and height is not None else 1080

    def as_object(self):
        """
        Return the object as a dictionary to allow serialising as JSON
        :return:
        """
        return {
            "id": str(self.id),
            "session": str(self.session),
            "derivedFrom": str(self.derivedFrom),
            "derivedAt": str(self.derivedAt),
            "width": self.width,
            "height": self.height
        }

    def get_postits(self):
        from src.model.Postit import Postit
        return Postit.get_by_property('canvas', self.id)

    @staticmethod
    def get_latest_canvas_by_session(sessionId, database=None):
        query = 'SELECT * FROM canvases WHERE session=\'{}\' ORDER BY datetime(derivedAt) ASC LIMIT 1 ;'.format(str(sessionId))
        if database:
            c = database.cursor()
        else:
            c = databaseHandler().get_database().cursor()

        c.execute(query)
        data = c.fetchone()

        if data is None:
            return None

        props = {}

        for i in range(len(Canvas.properties)):
            props[Canvas.properties[i]] = str(data[i])

        return Canvas(**props)

    def clone(self):
        postits = self.get_postits()

        new_canvas_id = uuid.uuid4()

        for postit in postits:
            postit.id = uuid.uuid4()
            postit.canvas = new_canvas_id
            postit.create()

        self.derivedAt = datetime.datetime.isoformat(datetime.datetime.now())
        self.derivedFrom = self.id
        self.id = new_canvas_id
        self.create()

        return self
