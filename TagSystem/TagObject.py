from PyAsoka.Core.AModel import AModel, DatabaseType


class TagObject(AModel):
    def __init__(self, id=None, reference=None):
        super(TagObject, self).__init__(self.DBProfile, self.DBTableName)

        self.id = self.IntField('id', id).PRIMARY_KEY().AUTOINCREMENT().NOT_NULL()
        self.reference = self.StrField('ref', reference).NOT_NULL()

        self.initialization()


TagObject.databaseSettings('asoka.db', DatabaseType.SQLITE, 'TagObjects')
