from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.src.Debug.Exceptions import Exceptions


class ObjectField:
    def __init__(self, obj, field):
        self.object = obj
        self.column = field.column
        self.autoload = field.autoload
        self.autosave = field.autosave
        self.loadOnRequest = field.loadOnRequest
        self.loaded = False
        self.value = field.defaultValue
        self.type = field.type

    def getter(self):
        if self.autoload or (self.loadOnRequest and not self.loaded):
            self.load()
        return self.value

    def setter(self, value):
        if isinstance(value, self.type):
            self.value = value
        else:
            try:
                self.value = self.type(value)
            except Exception as e:
                Exceptions.UnsupportableType(value)
        self.object.updated = True

        if self.autosave:
            self.save()

    def decode(self, value):
        try:
            self.value = self.type(value)
        except Exception as e:
            Logs.warning(f'ObjectField.fromDatabase: '
                         f'Не удалось привести значение ({type(value)}) к заданному типу ({self.type}): {e}')
        self.loaded = True

    def encode(self):
        return self.value

    def load(self):
        obj_id = self.object._id_
        if obj_id is not None:
            database = self.object.scheme.database
            database.connect(self.object.scheme.profile)
            data = database.query(f'SELECT {self.column.name} FROM {self.object.table.name} WHERE id=?', [obj_id])
            self.decode(data[self.column.name])

    def save(self):
        obj_id = self.object._id_
        if obj_id is not None:
            database = self.object.scheme.database
            database.connect(self.object.scheme.profile)
            database.execute(f'UPDATE {self.object.table.name} SET {self.column.name}=? '
                             f'WHERE id=?;', [self.encode(), obj_id])


class ObjectOneToOne:
    def __init__(self, obj, reference):
        self.object = obj
        self.column = reference.column
        self.name = reference.name
        self.model = reference.model
        self.value = None
        self.type = int
        self.id = None
        self.value = reference.defaultValue
        self.autoload = reference.autoload
        self.autosave = reference.autosave

    def idGetter(self):
        return self.id

    def idSetter(self, value):
        self.id = value

    def valueGetter(self):
        self.value = self.model(id=self.id).load()
        return self.value

    def valueSetter(self, obj):
        self.id = obj._id_
        self.value = obj
        obj.save()

    def decode(self, value):
        if value is not None:
            self.id = int(value)
        else:
            self.id = None

    def encode(self):
        return self.id


class ObjectOneToMany:
    def __init__(self, obj, field):
        self.object = obj
        self.model = field.model
        self.column = field.column

    def getter(self):
        scheme = self.model.scheme
        table = scheme.table
        database = scheme.database

        database.connect(scheme.profile)
        data = database.query(f'SELECT * FROM {table.name} WHERE {self.column.name}=?;', [self.object._id_])
        result = []
        if data is not False:
            for row in data:
                obj = self.model()
                obj.loadFromDBDict(row)
                result.append(obj)
        return result


class ObjectManyToMany:
    def __init__(self, obj, field):
        self.object = obj
        self.model = field.model
        self.scheme = field.scheme
        self.column = field.column
        self.refColumn = field.refColumn

    def getter(self):
        scheme = self.scheme
        table = scheme.table
        database = scheme.database

        database.connect(scheme.profile)
        data = database.query(f'SELECT * FROM {table.name} WHERE {self.column.name}=?;', [self.object._id_])
        if len(data) == 0:
            return []

        args = ''
        values = []
        for i in range(len(data)):
            if i == 0:
                args += 'id=? '
            else:
                args += 'OR id=? '
            values.append(data[i][self.refColumn.name])

        data = database.query(f'SELECT * FROM {self.model.scheme.table.name} WHERE {args};', values)
        result = []
        if data is not False:
            for row in data:
                obj = self.model()
                obj.loadFromDBDict(row)
                result.append(obj)
        return result

    def add(self, obj):
        scheme = self.scheme
        table = scheme.table
        database = scheme.database

        obj.save()

        database.connect(scheme.profile)
        database.execute(f'INSERT INTO {table.name}({self.column.name}, {self.refColumn.name}) VALUES(?, ?);',
                         [self.object._id_, obj._id_])
