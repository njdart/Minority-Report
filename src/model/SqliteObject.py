<<<<<<< HEAD
class SqliteObject(object):
    def __init__(self, properties, table, id=None, databaseHandler=None):
        self.properties = properties
        self.table = table
        self.databaseHandler = databaseHandler
        self.id = id

    @staticmethod
    def from_database_tuple(tuple, databaseHandler):
        raise NotImplementedError('Abstract SQL Object cannot be made from a tuple')
=======
from src.server import databaseHandler
import uuid


class SqliteObject(object):

    properties = []
    table = ""

    def __init__(self, id=None, database=None):

        self.id = id if id is not None else uuid.uuid4()
        self.database = database
>>>>>>> master

    def get_id(self):
        return self.id

    def as_object(self):
<<<<<<< HEAD
        raise NotImplementedError('Abstract SQL Object cannot be represented as an object')
=======
        props = {}
        for prop in self.properties:
            if hasattr(self, prop):
                if prop is not None:
                    props[prop] = str(getattr(self, prop))
                else:
                    props[prop] = None

        return props

    @classmethod
    def get_all(cls, database=None):
        query = 'SELECT * FROM {};'.format(cls.table)

        print('Using SELECT query {}'.format(query))

        if database:
            c = database.cursor()
        else:
            c = databaseHandler().get_database().cursor()

        c.execute(query)
        found = []
        rows = c.fetchall()
        for row in rows:
            props = {}

            for i in range(len(cls.properties)):
                props[cls.properties[i]] = row[i]

            found.append(cls(**props))

        return found
>>>>>>> master

    def update(self):
        if not self.databaseHandler:
            raise Exception('No Database Provided to Update in')

<<<<<<< HEAD
        set = []
=======
        print('Using SELECT query {}'.format(query))

        if database:
            c = database.cursor()
        else:
            c = databaseHandler().get_database().cursor()

        c.execute(query)
        data = c.fetchone()
        props = {}

        if data is None:
            return None

        for i in range(len(cls.properties)):
            props[cls.properties[i]] = str(data[i])

        return cls(**props)

    @classmethod
    def get_by_property(cls, prop, value, database=None, limit=10):
        """
        There are many security holes in this function
        the query is not sanitised, offering SQL injection vulns
        if the result is large, that could offer an entry point for DDOS
        please fix me
        """
        query = "SELECT * FROM {} WHERE {}='{}';".format(cls.table, prop, value)

        print('Using SELECT query {}'.format(query))

        if database:
            c = database.cursor()
        else:
            c = databaseHandler().get_database().cursor()

        c.execute(query)
        data = c.fetchall()

        if data is None:
            return None

        prop_list = []
        for result in range(len(data)):
            props = {}
            for prop in range(len(cls.properties)):
                props[cls.properties[prop]] = str(data[result][prop])
            prop_list.append(cls(**props))

        return prop_list


    def update(self, database=None):

        props = []
>>>>>>> master
        for property in self.properties:
            if property == 'id':
                continue

            set.append('{}=\'{}\''.format(property, getattr(self, property)))

        query = 'UPDATE {} SET {} WHERE id=?;'.format(self.table, ','.join(set))

        print('Using UPDATE query \'{}\''.format(query))
        c = self.databaseHandler.database.cursor()
        c.execute(query, (self.id,))
        self.databaseHandler.database.commit()
        return self

    def delete(self):
        if not self.databaseHandler:
            raise Exception('No Database Provided to Delete in')

        query = 'DELETE FROM {} WHERE id=?;'.format(self.table)

        print('Using DELETE query \'{}\''.format(query))

        c = self.databaseHandler.database.cursor()
        c.execute(query, (self.id,))
        self.databaseHandler.database.commit()

        return True

    @classmethod
    def delete_all(cls, database=None):
        query = 'DELETE FROM {};'.format(cls.table)

        print('Using DELETE query \'{}\''.format(query))

        if not database:
            database = databaseHandler().get_database()

        c = database.cursor()

        c.execute(query)
        database.commit()

        return True

    def create(self, databaseHandler=None):
        if not databaseHandler and not self.databaseHandler:
            raise Exception('No Database Provided to create in')

        properties = [str(p) for p in self.properties if getattr(self, p) != None]

        values = []
        selectors = []
        for property in self.properties:
            if hasattr(self, property):
                attr = getattr(self, property)
                if attr is not None:
                    if attr is None:
                        values.append(None)
                    if type(attr) in [int, float]:
                        values.append(str(attr))
                    else:
                        values.append('\'' + str(attr) + '\'')
                    selectors.append('{}=\'{}\''.format(property, str(attr)))

        query = 'INSERT INTO {} ({}) VALUES ({});'.format(self.table,
                                                          ','.join(properties),
                                                          ','.join(values))

        print('Using CREATE query \'{}\''.format(query))

        c = self.databaseHandler.database.cursor()
        c.execute(query)
        self.databaseHandler.database.commit()
        if not self.id:
            self.id = c.lastrowid

        return self
<<<<<<< HEAD
=======

    def __str__(self):
        return self.table + " row object with id " + str(self.get_id())
>>>>>>> master
