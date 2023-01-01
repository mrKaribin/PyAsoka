from PyAsoka.Instruments import Log
from PyAsoka.src.MVC.Model.Model import Model, DatabaseType


class Tag(Model):

    def __init__(self, id=None, name=None):
        super(Tag, self).__init__(self.DBProfile, self.DBTableName)

        self.id = self.IntField('id', id).PRIMARY_KEY().AUTOINCREMENT().NOT_NULL()
        self.name = self.StrField('name', name).NOT_NULL().UNIQUE()

        self.initialization()

    @staticmethod
    def create(name: str, _format: str):
        tag = Tag()
        tag.name.set(name)
        tag.save()
        return tag if tag.exist_in_database else None

    @staticmethod
    def fromDatabase(key, create=False):
        tag = Tag()
        if isinstance(key, int):
            tag.id.set(key)
            tag.load()
        elif isinstance(key, str):
            results = tag.find(f'name = "{key}"')
            if len(results) > 0:
                tag = results[0]
            else:
                if create:
                    tag = Tag(name=key)
                    tag.save()
                    return tag
                else:
                    return None
        else:
            Log.exception_unsupportable_type(type(key))
        return tag

    @staticmethod
    def fromString(string):
        from PyAsoka.Database.SqLite import SqLite as database
        database.connect(Tag.DBProfile)
        data = database.query(f'SELECT * FROM Tags WHERE name like "%{string}%"')
        tags = []
        for row in data:
            tag = Tag(row['id'], row['name'])
            tag.exist_in_database = True
            tags.append(tag)
        return tags

    @staticmethod
    def getAll():
        from PyAsoka.Database.SqLite import SqLite as database
        database.connect(Tag.DBProfile)
        data = database.query('SELECT * FROM Tags;')
        tags = []
        if data is not False:
            for row in data:
                tag = Tag(row['id'], row['name'])
                tag.exist_in_database = True
                tags.append(tag)
        return tags


Tag.databaseSettings('asoka.db', DatabaseType.SQLITE, 'Tags')
