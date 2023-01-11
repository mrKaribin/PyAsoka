from PyAsoka.src.MVC.Model.Model import Model, DatabaseType
from PyAsoka.src.Instruments.File import File as OsFile
from PyAsoka.TagSystem.TagObject import TagObject
from PyAsoka.Instruments import Log


class File(Model):

    def __init__(self, id=None, name=None, data=None, format=None):
        super(File, self).__init__(self.DBProfile, 'Files')

        self.id = self.IntField('id', id).PRIMARY_KEY().AUTOINCREMENT().NOT_NULL()
        self.object = self.AField('object', TagObject.DBTableName, 'id', TagObject, TagObject(reference=self.DBTableName))
        self.name = self.StrField('name', name).NOT_NULL()
        self.data = self.BlobField('data', data, load=False).NOT_NULL()
        self.format = self.StrField('format', format).DEFAULT('txt').NOT_NULL()

        self.initialization()

    @staticmethod
    def create(name: str, data, _format: str):
        file = File()
        file.name.set(name)
        file.data.set(data)
        file.data.set(data)
        file.format.set(_format)
        file.save()
        return file

    @staticmethod
    def fromPath(_file, name=None):
        if isinstance(_file, str):
            _file = OsFile(_file)
        if isinstance(_file, OsFile):
            file = File()
            if name is None:
                file.name.set(_file.stem)
            else:
                file.name.set(name)
            file.format.set(_file.suffix)
            file.data.set(_file.read_bytes())
            file.save()
            return file
        else:
            Log.exception_unsupportable_type(type(_file))


    @staticmethod
    def fromId(_id):
        file = File()
        file.id.set(_id)
        file.load()
        return file

    @staticmethod
    def findByFilters(name_contains: str = None, tags: list = None):
        from PyAsoka.src.Database.SqLite import SqLite as database
        from PyAsoka.TagSystem.Tag import Tag
        query = f'SELECT id FROM Files WHERE '

        if isinstance(tags, list) and len(tags) > 0:
            for tag in tags:
                if isinstance(tag, Tag):
                    tag_id = tag.id()
                elif isinstance(tag, int):
                    tag_id = tag
                else:
                    Log.exception_unsupportable_type(type(tag))
                query += f'object IN (SELECT obj_id FROM TagLinks WHERE tag_id = {tag_id}) AND '

        if name_contains is not None:
            query += f'name like "%{name_contains}%" AND '

        query = query[:-5] + ';'
        data = database.query(query)
        return [File.fromId(row['id']) for row in data]

    @staticmethod
    def getAll(limit=50, order_by='name'):
        from PyAsoka.src.Database.SqLite import SqLite as database
        from PyAsoka.FileSystem.FileType import FileType
        database.connect(File.DBProfile)
        data = database.query(f'SELECT id, format FROM Files ORDER BY {order_by} LIMIT {limit};')
        files = []
        for row in data:
            filetype = FileType.fromSuffix(row['format'])
            file = filetype.handler()
            file.id.set(row['id'])
            file.load()
            files.append(file)
        return files


File.databaseSettings('asoka.db', DatabaseType.SQLITE, 'Files')
