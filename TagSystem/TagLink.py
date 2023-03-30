from PyAsoka.src.MVC.ModelOld.Model import Model, DatabaseType
from PyAsoka.Instruments import Log


class TagLink(Model):

    def __init__(self, id=None, tag_id=None, obj_id=None):
        super(TagLink, self).__init__(self.DBProfile, self.DBTableName)

        self.id = self.IntField('id', id).PRIMARY_KEY().AUTOINCREMENT().NOT_NULL()
        self.tag_id = self.IntField('tag_id', tag_id).NOT_NULL().REFERENCE('Tags', 'id')
        self.obj_id = self.IntField('obj_id', obj_id).NOT_NULL().REFERENCE('Files', 'id')

        self.initialization()

    @staticmethod
    def create(tag_id: int, obj_id: int):
        link = TagLink()
        link.tag_id.set(tag_id)
        link.obj_id.set(obj_id)
        link.save()
        return link

    @staticmethod
    def fromId(_id: int):
        link = TagLink()
        link.id.set(_id)
        link.load()
        return link

    @staticmethod
    def findByTag(tag):
        from PyAsoka.TagSystem.Tag import Tag
        tag_id = None

        if isinstance(tag, Tag):
            tag_id = tag.id()
        elif isinstance(tag, int):
            tag_id = tag
        else:
            Log.exception_unsupportable_type(type(tag))

        tags = TagLink().find(f'tag_id = {tag_id}')
        return tags

    @staticmethod
    def findByFile(file):
        from PyAsoka.FileSystem.File import File
        obj_id = None

        if isinstance(file, File):
            obj_id = file.object().id()
        elif isinstance(file, int):
            obj_id = file
        else:
            Log.exception_unsupportable_type(type(file))

        tags = TagLink().find(f'obj_id = {obj_id}')
        return tags


TagLink.databaseSettings('asoka.db', DatabaseType.SQLITE, 'TagLinks')
