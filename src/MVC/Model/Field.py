from PyAsoka.Debug import Exceptions


class Field:
    def __init__(self, database, table, datatype, autoload: bool = False, autosave: bool = False):
        self.autoload = autoload
        self.autosave = autosave
        self.type = datatype
        self.value = None
        self.name = 'default'

        self.database = database
        self.table = table
        self.column = self.database.Column(self.name, self.database.Column.toSqlType(self.type))
        self.table.columns.append(self.column)

    def setName(self, name):
        self.name = name
        self.column.name = name

    def PRIMARY_KEY(self):
        self.column.PRIMARY_KEY()
        return self

    def AUTOINCREMENT(self):
        self.column.AUTOINCREMENT()
        return self

    def UNIQUE(self):
        self.column.UNIQUE()
        return self

    def NOT_NULL(self):
        self.column.NOT_NULL()
        return self

    def DEFAULT(self, value):
        self.column.DEFAULT(value)
        return self

    def CHECK(self, condition):
        self.column.CHECK()
        return self

    def fromSql(self, value):
        if type(value) in (int, str, bool, float):
            return self.type(value)


class ReferenceField(Field):
    def __init__(self, database, table, cls, field, autoload: bool = False, autosave: bool = False):
        if isinstance(field, Field):
            pass
        elif isinstance(field, str):
            field = cls.fields[field]
        else:
            raise Exceptions.UnsupportableType(field)

        super().__init__(database, table, cls.containerType, autoload, autosave)
        self.ref_class = cls
        self.ref_field = field
        self._on_update_ = None
        self._on_delete_ = None

    def setName(self, name):
        self.name = name
        self.column.name = name + 'Id'

    def ON_UPDATE_CASCADE(self):
        self._on_update_ = 'CASCADE'

    def ON_UPDATE_RESTRICT(self):
        self._on_update_ = 'CASCADE'

    def ON_UPDATE_SET_NULL(self):
        self._on_update_ = 'SET NULL'

    def ON_UPDATE_SET_DEFAULT(self):
        self._on_update_ = 'SET DEFAULT'

    def ON_DELETE_CASCADE(self):
        self._on_delete_ = 'CASCADE'

    def ON_DELETE_RESTRICT(self):
        self._on_delete_ = 'CASCADE'

    def ON_DELETE_SET_NULL(self):
        self._on_delete_ = 'SET NULL'

    def ON_DELETE_SET_DEFAULT(self):
        self._on_delete_ = 'SET DEFAULT'