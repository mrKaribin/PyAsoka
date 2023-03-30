from PyAsoka.src.Instruments.Timepoint import Timepoint
from PyAsoka.src.Database.DatabaseProfile import DatabaseProfile
from PyAsoka.src.MVC.ModelOld.Field import Field, ReferenceField


class ModelConfiguration:

    def __init__(self, profile: DatabaseProfile, table_name: str):
        self.profile = profile
        self.database = self.profile.getDriver()
        self.table = self.database.Table(self.profile, table_name)

    def addField(self, datatype, autoload: bool = False, autosave: bool = False):
        return Field(self.database, self.table, datatype, autoload, autosave)

    def IntField(self, autoload: bool = False, autosave: bool = False):
        return self.addField(int, autoload, autosave)

    def FloatField(self, autoload: bool = False, autosave: bool = False):
        return self.addField(float, autoload, autosave)

    def StrField(self, autoload: bool = False, autosave: bool = False):
        return self.addField(str, autoload, autosave)

    def BoolField(self, autoload: bool = False, autosave: bool = False):
        return self.addField(bool, autoload, autosave)

    def BlobField(self, autoload: bool = False, autosave: bool = False):
        return self.addField(bool, autoload, autosave)

    def TimepointField(self, autoload: bool = False, autosave: bool = False):
        return self.addField(Timepoint, autoload, autosave)

    def Reference(self, cls, field, autoload: bool = False, autosave: bool = False):
        return ReferenceField(self.database, self.table, cls, field, autoload, autosave)