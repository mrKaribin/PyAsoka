from copy import deepcopy
from enum import Enum, auto

from PyAsoka.Debug.Logs import Logs
from PyAsoka.Instruments.ATimepoint import ATimepoint
from PyAsoka.Database.ADatabaseProfile import ADatabaseProfile, DatabaseType

import inspect


def model(cls):
    if getattr(cls, "static_init", None):
        cls.static_init()
    return cls


class AField:
    def __init__(self, database, table, datatype, autoload: bool = True, autosave: bool = True):
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

    def REFERENCE(self, table, column):
        # self.model.REFERENCE(self, table, column) ToDo
        return self

    def fromSql(self, value):
        if type(value) in (int, str, bool, float):
            return self.type(value)


class AObjectField:
    def __init__(self, obj, field: AField, value):
        self.object = obj
        self.column = field.column
        self.database = self.object.database
        self.type = field.type
        self.value = value
        self.autoload = field.autoload
        self.autosave = field.autosave

        self.object.fields[self.column.name] = self
        # self.object.table.columns.append(self.column)

    def __call__(self):
        return self.get(self)

    def set(self, obj, value):
        if isinstance(value, self.type):
            self.value = value
            if self.autosave and self.object.exist_in_database:
                self.save()
        else:
            Logs.exception_unsupportable_type(value)

    def get(self, obj):
        if self.autoload and self.object.exist_in_database:
            self.load()
        return self.value

    def distinct(self):
        self.database.connect(self.object.table.profile)
        if (data := self.database.query(f'SELECT DISTINCT {self.column.name} FROM {self.object.table.name};')) is not False:
            return [row[self.column.name] for row in data]

    def empty(self):
        return self.value is None

    def load(self):
        pass

    def save(self):
        pass


class DataArray:
    def __init__(self, _type, objects: list):
        self.type = _type
        self.objects = objects

    def get(self, **kwargs):
        pass

    def first(self):
        return self.objects[0]


class Selector:
    def __init__(self, _type):
        self.type = _type
        self.database = _type.settings.database
        self.table = _type.settings.table
        self.fields = _type.fields
        self._where_ = {}
        self._limit_ = None
        self._offset_ = None

    def __getitem__(self, item):
        if isinstance(item, slice):
            if item.start != 0:
                self._offset_ = item.start
            else:
                item.start = 0
            if item.stop != 0:
                self._limit_ = item.stop - item.start

        if isinstance(item, int):
            self._limit_ = 1
            self._offset_ = item

        return self

    def clear(self):
        self._where_ = {}
        self._limit_ = None
        self._offset_ = None

    def __add_compare__(self, key, arg, _type):
        field = self.fields[key]
        if field is not None:
            self._where_[key] = [_type, arg]
        else:
            Logs.warning(f'Модель "{self.table.name}" не имеет поля "{key}"')

    def __where__(self):
        if len(self._where_) > 0:
            where, values = ' WHERE ', []

            for key, data in self._where_.items():
                compare, value = data
                where += f'{key}{compare}?, '
                values.append(value)
            where = where[:len(where) - 2]

            return where, values
        else:
            return '', []

    def __limit__(self):
        if self._limit_ is not None:
            lim = f' LIMIT {self._limit_}'
            if self._offset_ is not None:
                lim += f' OFFSET {self._offset_}'
            return lim
        else:
            return ''

    def filter(self, **kwargs):
        for key, arg in kwargs.items():
            if isinstance(arg, tuple) or isinstance(arg, list):
                compare, arg = arg
                self.__add_compare__(key, arg, compare)
            else:
                self.__add_compare__(key, arg, '=')
        return self

    def create(self, **kwargs):
        cols, vals, params = '', '', []
        for key, value in kwargs.items():
            field = self.fields[key]
            if field is not None:
                cols += key + ', '
                vals += f'?, '
                params.append(value)
        cols, vals = cols[:len(cols) - 2], vals[:len(vals) - 2]
        self.database.connect(self.table.profile)
        if self.database.execute(f'INSERT INTO {self.table.name} ({cols}) VALUES ({vals});', list(params)):
            self.clear()
            return self.filter(id=self.database.getLastAutoincrement(self.table.name)).get()
        else:
            return False

    def get(self, *args):
        data = self.getDict(*args)
        args = {}
        for row in data:
            for key, arg in row.items():
                args[key] = self.fields[key].fromSql(arg)
        objects = self.type.containerType(**args)
        return objects

    def getDict(self, *args):
        where, where_vals = self.__where__()
        limit = self.__limit__()

        if len(args) == 0:
            keys, all_keys = '', True
            for field in self.fields.values():
                if field.autoload:
                    keys += field.column.name + ', '
                else:
                    all_keys = False
            if all_keys:
                keys = '*'
            elif len(keys) > 0:
                keys = keys[:len(keys) - 2]
        else:
            keys = ''
            for key in args:
                fld = self.fields[key]
                if fld is not None:
                    keys += fld.column.name + ', '
            if len(keys) > 0:
                keys = keys[:len(keys) - 2]

        self.database.connect(self.table.profile)
        return self.database.query(f'SELECT {keys} FROM {self.table.name}{where}{limit};', where_vals)

    def set(self, **kwargs):
        where, where_vals = self.__where__()
        limit = self.__limit__()

        changes = ''
        change_vals = []
        for key, arg in kwargs.items():
            fld = self.fields[key]
            if fld is not None:
                changes += f'{key}=?, '
                change_vals.append(arg)
        if len(changes) > 0:
            changes = changes[:len(changes) - 2]

        self.database.connect(self.table.profile)
        self.database.query(f'UPDATE {self.table.name} SET {changes}{where}{limit};', [*change_vals, *where_vals])

    def delete(self):
        where, where_vals = self.__where__()
        limit = self.__limit__()

        self.database.connect(self.table.profile)
        self.database.query(f'DELETE FROM {self.table.name}{where}{limit};', where_vals)

    def exists(self):
        objs = self.getDict('id')
        return objs


class AModelContainer(object):
    _fields_ = {}

    model = None
    database = ADatabaseProfile(DatabaseType.SQLITE, 'tests.db', 'root', '').getDriver()
    table = database.Table(database.profile, 'Default')

    def __init__(self, **kwargs):
        self.exist_in_database = False
        self.fields = {}
        for field in self._fields_.values():
            name = field.column.name
            if name in kwargs.keys():
                value = kwargs[name]
            else:
                value = None
            attr = AObjectField(self, field, value)

            setattr(self.__class__, name, property(attr.get, attr.set))

    def __str__(self):
        return self.print()

    def print(self, indent_size=0):
        indent = ''
        for i in range(indent_size):
            indent += ' '
        result = f'\n{indent}class {self.__class__.__name__} || id: {self.fields["id"].value}'
        for field in self.fields.values():
            result += f'\n    {indent}({type(field.value)}) {field.column.name}: ' \
                      f'{field() if not issubclass(field.type, AModelContainer) else field().print(indent_size + 4)}'
        return result

    def insert(self):
        args = {}
        for field in self.fields.values():
            if isinstance(field, AObjectField) and field.value is not None and field.column.name != 'id':
                args[field.column.name] = field.value
        obj = self.model.objects().create(**args)
        if obj is not False:
            self.fields['id'].set(self, obj.id)

    def update(self):
        args = {}
        for field in self.fields.values():
            if not (not field.autoload and field.value is None) and not field.column.name == 'id':
                args[field.column.name] = field.value
        self.model.objects().filter(id=self.id).set(**args)
        return self

    def exists(self):
        if not self.exist_in_database:
            self.exist_in_database = self.model.objects().filter(id=self.id).exists()
        return self.exist_in_database

    def save(self):
        if self.exists():
            self.update()
        else:
            self.insert()
        return self

    def load(self):
        data = self.model.objects().filter(id=self.id).getDict()
        if data:
            data = data[0]
            for key, value in data.items():
                field = self.fields[key]
                if field is not None:
                    field.value = self._fields_[key].fromSql(value)
        return self

    def delete(self):
        self.model.objects().filter(id=self.id).delete()
        return self


class ModelSettings:

    def __init__(self, profile: ADatabaseProfile, table_name: str):
        self.profile = profile
        self.database = self.profile.getDriver()
        self.table = self.database.Table(self.profile, table_name)

    def addField(self, datatype, autoload: bool = True, autosave: bool = True):
        return AField(self.database, self.table, datatype, autoload, autosave)

    def IntField(self, autoload: bool = True, autosave: bool = True):
        return self.addField(int, autoload, autosave)

    def FloatField(self, autoload: bool = True, autosave: bool = True):
        return self.addField(float, autoload, autosave)

    def StrField(self, autoload: bool = True, autosave: bool = True):
        return self.addField(str, autoload, autosave)

    def BoolField(self, autoload: bool = True, autosave: bool = True):
        return self.addField(bool, autoload, autosave)

    def BlobField(self, autoload: bool = True, autosave: bool = True):
        return self.addField(bool, autoload, autosave)

    def TimepointField(self, autoload: bool = True, autosave: bool = True):
        return self.addField(ATimepoint, autoload, autosave)


@model
class AModel:
    DatabaseType = DatabaseType
    DatabaseProfile = ADatabaseProfile
    settings = ModelSettings(DatabaseProfile(DatabaseType.SQLITE), '')
    fields = {}
    containerType = None

    @classmethod
    def static_init(cls):
        print('\n', cls.__name__)
        cls.fields = {}
        cls.id = cls.settings.IntField().PRIMARY_KEY().AUTOINCREMENT().NOT_NULL()
        for field in inspect.getmembers(cls, lambda value: isinstance(value, AField)):
            print(field)
            name, field = field
            field.setName(name)
            cls.fields[field.name] = field
        if len(cls.fields) > 1:
            if not cls.settings.table.isExist():
                cls.settings.table.create()
            cls.containerType = cls.create_type()

    @classmethod
    def createSettings(cls, profile: ADatabaseProfile, table_name: str):
        return ModelSettings(profile, table_name)

    @classmethod
    def ForeignKey(cls, name: str, table_name: str, datatype, autoload: bool = True, autosave: bool = True):
        field = cls.addField(cls.database, datatype, name, autoload, autosave)
        cls.REFERENCE(name, table_name, 'id')
        return field

    @classmethod
    def REFERENCE(cls, key, table, column='id'):
        if isinstance(key, AField):
            key = key.column.name
        if issubclass(type(table), AModel):
            table = table.table.profile.table
        if isinstance(column, AField):
            column = column.column.name

        ref = cls.database.Reference(key, table, column)
        cls.table.references.append(ref)
        return ref

    @classmethod
    def create_type(cls):
        fields = {
            'model': cls,
            '_fields_': cls.fields,
            'database': cls.settings.database,
            'table': cls.settings.table
        }

        _type = type(f'{cls.settings.table.name}Object', (AModelContainer,), fields)
        return _type

    @classmethod
    def objects(cls):
        return Selector(cls)

    @classmethod
    def instance(cls, **kwargs):
        return cls.containerType(**kwargs)

    def find_reference(self, key: str):
        for ref in self.table.references:
            if ref.key == key:
                return ref

    @staticmethod
    def isContainerType(obj):
        return issubclass(type(obj), AModelContainer)

    @staticmethod
    def isModelType(obj):
        return issubclass(type(obj), AModel)
