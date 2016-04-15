from src.server import databaseHandler

class SqliteObject(object):

    properties = []
    table = ""

    def __init__(self, id=None, database=None):
        self.id = id
        self.database = database

    def get_id(self):
        return id

    def as_object(self):
        props = {}
        for prop in self.properties:
            if hasattr(self, prop):
                props[prop] = getattr(self, prop)

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

    @classmethod
    def get(cls, id, database=None):
        query = 'SELECT * FROM {} WHERE id={};'.format(cls.table, id)

        print('Using SELECT query {}'.format(query))

        if database:
            c = database.cursor()
        else:
            c = databaseHandler().get_database().cursor()

        c.execute(query)
        data = c.fetchone()
        props = {}
        for i in range(len(cls.properties)):
            props[cls.properties[i]] = data[i]

        return cls(**props)


    def update(self):
        if not self.databaseHandler:
            raise Exception('No Database Provided to Update in')

        set = []
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

        return self

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
                    values.append(attr)
                    selectors.append('{}=\'{}\''.format(property, str(attr)))

        query = 'INSERT INTO {} ({}) VALUES ({});'.format(self.table,
                                                          ','.join(properties),
                                                          ','.join(map(lambda x: '\'' + str(x) + '\'', values)))

        print('Using CREATE query \'{}\''.format(query))

        c = self.databaseHandler.database.cursor()
        c.execute(query)
        self.databaseHandler.database.commit()
        if not self.id:
            self.id = c.lastrowid

        return self
