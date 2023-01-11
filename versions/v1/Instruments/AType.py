from copy import deepcopy

from PyAsoka.Instruments import Log
from PyAsoka.src.Instruments.Timepoint import Timepoint
from PyAsoka.src.Database.DatabaseProfile import DatabaseProfile, DatabaseType


class AField:
    def __init__(self, model, datatype, name: str, value=None,
                 autoload: bool = False, autosave: bool = False, load=True):
        self.model = model
        self.autoload = autoload
        self.autosave = autosave
        self.default_load = load
        self.type = datatype
        self.value = value

        self.database = self.model.database
        self.column = self.database.Column(name, self.database.Column.toSqlType(datatype))
        self.model.fields.append(self)
        self.model.table.columns.append(self.column)

    def __call__(self):
        if self.autoload and self.model.exist_in_database:
            self.load()
        if self.value is None and not self.default_load and self.model.exist_in_database:
            self.load()
        return self.value

    def set(self, value):
        if isinstance(value, self.type):
            self.value = value
            if self.autosave and self.model.exist_in_database:
                self.save()
        else:
            Log.exception_unsupportable_type(value)

    def empty(self):
        return self.value is None

    def toSql(self):
        if self.value is None:
            return None

        elif self.type in (int, float, bool, str, bytes):
            return self.value

        elif self.type == Timepoint:
            return self.value.encode()

        elif issubclass(self.type, AType):
            self.value.save()
            ref = self.model.find_reference(self.column.name)
            value = 0
            for field in self.value.fields:
                if field.column.name == ref.column:
                    value = field.toSql()
            return value

        else:
            return None

    def fromSql(self, data):
        if data is None:
            self.value = None

        elif self.type in (str, bytes, int, float, bool):
            self.set(self.type(data))

        elif self.type == Timepoint:
            self.set(Timepoint.decode(data))

        elif issubclass(self.type, AType):
            obj = self.type()
            ref = self.model.find_reference(self.column.name)

            for field in obj.fields:
                if field.column.name == ref.column:
                    field.fromSql(data)
                    break
            row = obj.table.row()
            row.load(f'{ref.column} = {field.toSql()}')
            obj.setRow(row)
            self.set(obj)

    def distinct(self):
        self.database.connect(self.model.table.profile)
        if (data := self.database.query(f'SELECT DISTINCT {self.column.name} FROM {self.model.table.name};')) is not False:
            return [row[self.column.name] for row in data]

    def PRIMARY_KEY(self):
        self.column.PRIMARY_KEY()
        self.model.primary_key = self
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

    def REFERENCE(self, table, column):
        self.model.REFERENCE(self, table, column)
        return self

    def load(self):
        self.database.connect(self.model.profile)
        data = self.database.query(f'SELECT {self.column.name} FROM {self.model.table.name} '
                                   f'WHERE {self.model.primary_key.column.name} = {self.model.primary_key.toSql()};')
        self.set(data[self.column.name])

    def save(self):
        self.database.connect(self.model.profile)
        self.database.execute(f'UPDATE {self.model.table} SET {self.column.name} = {self.toSql()} '
                              f'WHERE {self.model.primary_key.column.name} = {self.model.primary_key.toSql()};')


class AType:
    DBName = ''
    DBTableName = ''
    DBProfile = DatabaseProfile(DatabaseType.SQLITE, DBName, 'root', '')

    def __init__(self, profile: DatabaseProfile, table_name):
        self.database = profile.getDriver()
        self.table = self.database.Table(profile, table_name)
        self.fields = []
        self.primary_key = None
        self.exist_in_database = False

    def initialization(self):
        if not self.table.isExist():
            self.table.create()

    def find(self, where: str, ):
        self.database.connect(self.table.profile)
        if (data := self.database.query(f'SELECT * FROM {self.table.name} WHERE {where};')) is not False:
            results = []
            for row in data:
                obj = deepcopy(self)
                for field in obj.fields:
                    field.set(row[field.column.name])
                results.append(obj)
            return results
        else:
            return []

    def __str__(self):
        return self.print()

    def print(self, indent_size=0):
        indent = ''
        for i in range(indent_size):
            indent += ' '
        result = f'\n{indent}class {self.__class__.__name__} || key: {self.primary_key.value}'
        for field in self.fields:
            result += f'\n    {indent}{field.column.name}: ' \
                      f'{field() if not issubclass(field._type_, AType) or field() is None else field().print(indent_size + 4)}'
        return result

    def REFERENCE(self, key, table, column):
        if isinstance(key, AField):
            key = key.column.name
        if issubclass(type(table), AType):
            table = table.table.profile.table
        if isinstance(column, AField):
            column = column.column.name

        ref = self.database.Reference(key, table, column)
        self.table.references.append(ref)
        return ref

    def IntField(self, name: str, value=None, autoload: bool = False, autosave: bool = False, load=True):
        return AField(self, int, name, value, autoload, autosave, load)

    def FloatField(self, name: str, value=None, autoload: bool = False, autosave: bool = False, load=True):
        return AField(self, float, name, value, autoload, autosave, load)

    def StrField(self, name: str, value=None, autoload: bool = False, autosave: bool = False, load=True):
        return AField(self, str, name, value, autoload, autosave, load)

    def BoolField(self, name: str, value=None, autoload: bool = False, autosave: bool = False, load=True):
        return AField(self, bool, name, value, autoload, autosave, load)

    def BlobField(self, name: str, value=None, autoload: bool = False, autosave: bool = False, load=True):
        return AField(self, bytes, name, value, autoload, autosave, load)

    def TimepointField(self, name: str, value=None, autoload: bool = False, autosave: bool = False, load=True):
        return AField(self, Timepoint, name, value, autoload, autosave, load)

    def AField(self, name: str, table_name: str, column_name: str, datatype, value=None, autoload: bool = False, autosave: bool = False, load=True):
        self.REFERENCE(name, table_name, column_name)
        return AField(self, datatype, name, value, autoload, autosave, load)

    def save(self):
        row = self.table.row(*[field.toSql() for field in self.fields])
        if self.primary_key.value is not None and row.exists(self.primary_key.column.name):
            state = row.update(f'{self.primary_key.column.name} = {self.primary_key.value}')
        else:
            key = row.insert()
            if key is not False:
                state = True
                if self.primary_key.column.autoincrement:
                    self.primary_key.set(self.primary_key._type_(key))
            else:
                state = False
        if state is True:
            self.exist_in_database = True

    def load(self):
        row_data = []
        for field in self.fields:
            if field.default_load:
                row_data.append((field.column, None))
        row = self.database.Row(self.table, *row_data)
        if row.load(f'{self.primary_key.column.name} = {self.primary_key.value}'):
            self.setRow(row)
            return True
        return False

    def delete(self, where: str = None):
        for field in self.fields:
            if issubclass(field._type_, AType):
                field().delete()
        row = self.table.row(*[field.toSql() if not issubclass(field._type_, AType) else None for field in self.fields])
        row.delete(where)

    def setRow(self, row):
        for field in self.fields:
            if field.column.name in row.keys():
                # print(field.column.name, row[field.column.name])
                field.fromSql(row[field.column.name])

    def find_reference(self, key: str):
        for ref in self.table.references:
            if ref.key == key:
                return ref

    @classmethod
    def databaseSettings(cls, database_name, database_type: DatabaseType, table_name, database_password=None):
        from PyAsoka import Asoka as a
        cls.DBName = database_name
        cls.DBTableName = table_name
        if database_password is None:
            database_password = a.getDatabasePassword(database_name)
        cls.DBProfile = DatabaseProfile(database_type, cls.DBName, 'root', database_password)
