from src.model.SqliteObject import SqliteObject


class Connection(SqliteObject):
    """
    A Connection object joins two stickyNotes together
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
        Represents a connection between two stickyNotes on a canvas
        :param start: the stickyNote to connect from
        :param finish: the stickyNote to connect to
        :param canvas: the canvas the stickyNotes are in
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
