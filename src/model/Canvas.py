from src.model.SqliteObject import SqliteObject
from src.server import databaseHandler
import uuid
import datetime


class Canvas(SqliteObject):
    """
    A Canvas object relates to a session and contains a size of the canvas to be displayed
    """

<<<<<<< HEAD
    def __init__(self,
                 image,
                 canvasBounds,
                 id=uuid.uuid4(),
                 postits=[],
                 connections=[],
                 derivedFrom=None,
                 derivedAt=datetime.datetime.now(),
                 databaseHandler=None):
=======
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
                 id=None,
                 stickyNotes=[],
                 connections=[],
                 derivedFrom=None,
                 derivedAt=datetime.datetime.now(),
                 width=None,
                 height=None,
                 ):
>>>>>>> master
        """
        :param session UUID v4 of session to which canvas belongs
        :param id UUID v4
        :param stickyNotes list of stickyNote objects or UUID v4s
        :param connections list of (stickyNote/stickyNoteUUID, stickyNote/stickyNoteUUID) tuples
        :param derivedFrom canvas object or ID this object derives from
        :param width integer width of HUD
        :param height integer height of HUD
        """
<<<<<<< HEAD
        super(Canvas, self).__init__(id=id,
                                     properties=[
                                         "image",
                                         "derivedFrom",
                                         "derivedAt",
                                         "canvasTopLeftX",
                                         "canvasTopLeftY",
                                         "canvasTopRightX",
                                         "canvasTopRightY",
                                         "canvasBottomLeftX",
                                         "canvasBottomLeftY",
                                         "canvasBottomRightX",
                                         "canvasBottomRightY"
                                     ],
                                     table="canvas",
                                     databaseHandler=databaseHandler)
        self.image = image

        canvasTopLeft = canvasBounds[0]
        self.canvasTopLeftX = canvasTopLeft[0]
        self.canvasTopLeftY = canvasTopLeft[1]

        canvasTopRight = canvasBounds[1]
        self.canvasTopRightX = canvasTopRight[0]
        self.canvasTopRightY = canvasTopRight[1]

        canvasBottomRight = canvasBounds[2]
        self.canvasBottomRightX = canvasBottomRight[0]
        self.canvasBottomRightY = canvasBottomRight[1]

        canvasBottomLeft = canvasBounds[3]
        self.canvasBottomLeftX = canvasBottomLeft[0]
        self.canvasBottomLeftY = canvasBottomLeft[1]

        self.postits = postits
=======
        super(Canvas, self).__init__(id=id)
        self.session = session
        self.stickyNotes = stickyNotes
>>>>>>> master
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
<<<<<<< HEAD
        get a postit by it's id"""
        for postit in self.postits:
            if type(postit) == int and postit == id:
                return self.databaseHandler.get_postit(id)
            elif postit.get_id() == id:
                return postit
        return None

    def add_connection(self, start, end):
        self.connections.append((start, end))

    def get_image(self):
        return self.image
=======
        return {
            "id": str(self.id),
            "session": str(self.session),
            "derivedFrom": str(self.derivedFrom),
            "derivedAt": str(self.derivedAt),
            "width": self.width,
            "height": self.height
        }

    def get_stickyNotes(self):
        from src.model.StickyNote import StickyNote
        return StickyNote.get_by_property('canvas', self.id)

    @staticmethod
    def get_latest_canvas_by_session(sessionId, database=None):
        query = 'SELECT * FROM canvases WHERE session=\'{}\' ORDER BY datetime(derivedAt) DESC LIMIT 1 ;'.format(str(sessionId))
        if database:
            c = database.cursor()
        else:
            c = databaseHandler().get_database().cursor()
>>>>>>> master

        c.execute(query)
        data = c.fetchone()

<<<<<<< HEAD
    def get_canvas_unkeystoned(self):
        return self.image[self.canvasTopLeftY:self.canvasBottomRightY, self.canvasTopLeftX:self.canvasBottomRightX]
=======
        if data is None:
            return None

        props = {}

        for i in range(len(Canvas.properties)):
            props[Canvas.properties[i]] = str(data[i])

        return Canvas(**props)

    def clone(self):
        stickyNotes = self.get_stickyNotes()

        new_canvas_id = uuid.uuid4()

        for stickyNote in stickyNotes:
            stickyNote.id = uuid.uuid4()
            stickyNote.canvas = new_canvas_id
            stickyNote.create()

        self.derivedAt = datetime.datetime.isoformat(datetime.datetime.now())
        self.derivedFrom = self.id
        self.id = new_canvas_id
        self.create()

        return self
>>>>>>> master
