from src.server import databaseHandler


class SqliteObject(object):

    properties = []
    table = ""

    def __init__(self, id=None, database=None):
        self.id = id
        self.database = database

    def get_id(self):
        return self.id

    def as_object(self):
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

    @classmethod
    def get(cls, id, database=None):
        query = 'SELECT * FROM {} WHERE id=\'{}\';'.format(cls.table, id)

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

    def update(self, database=None):

        props = []
        for property in self.properties:
            if property == 'id':
                continue

            props.append('{}=\'{}\''.format(property, getattr(self, property)))

        query = 'UPDATE {} SET {} WHERE id=?;'.format(self.table, ','.join(props))

        print('Using UPDATE query \'{}\''.format(query))

        if self.database:
            db = self.database
        elif database:
            db = database
        else:
            db = databaseHandler().get_database()

        c = db.cursor()
        c.execute(query, (self.id,))
        db.commit()
        return self

    def delete(self, database=None):

        query = 'DELETE FROM {} WHERE id=?;'.format(self.table)

        print('Using DELETE query \'{}\''.format(query))

        if self.database:
            db = self.database
        elif database:
            db = database
        else:
            db = databaseHandler().get_database()

        c = db.cursor()
        c.execute(query, (self.id,))
        db.commit()

        return True

    def create(self, database=None):

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

        if self.database:
            db = self.database
        elif database:
            db = database
        else:
            db = databaseHandler().get_database()

        c = db.cursor()
        c.execute(query)
        db.commit()
        if not self.id:
            self.id = c.lastrowid

        return self

    def __str__(self):
        return self.table + " row object with id " + str(self.get_id())