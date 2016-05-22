from src.model.SqliteObject import SqliteObject
import uuid
import datetime


class Connection(SqliteObject):
    """
    A Connection object joins two postits together
    """

    properties = [
        "id",
        "start",
        "finish",
        "canvas",
        "type"
    ]

    table = "connections"

    def __init__(self,
                 start,
                 finish,
                 canvas,
                 type=None,
                 id=None):
        """
        Represents a connection between two postits on a canvas
        :param start: the postit to connect from
        :param finish: the postit to connect to
        :param canvas: the canvas the postits are in
        :param type: the type (currently only None)
        :param id: the id of the connection
        """
        super(Connection, self).__init__(id=id)
        self.start = start
        self.finish = finish
        self.canvas = canvas
        self.type = type

    def as_object(self):
        """
        Return the object as a dictionary to allow serialising as JSON
        :return:
        """
        return {
            "id": str(self.id),
            "start": self.start,
            "finish": self.finish,
            "canvas": self.canvas,
            "type": self.type
        }
