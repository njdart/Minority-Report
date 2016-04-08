class SqliteObject(object):
    def __init__(self, properties, table, databaseHandler=None):
        self.properties = properties
        self.table = table
        self.databaseHandler = databaseHandler
        self.id = None

    @staticmethod
    def from_database_tuple(tuple, databaseHandler):
        raise NotImplementedError('Abstract SQL Object cannot be made from a tuple')

    def id(self):
        return id

    def as_object(self):
        raise NotImplementedError('Abstract SQL Object cannot be represented as an object')

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
        self.id = c.lastrowid

        return self
