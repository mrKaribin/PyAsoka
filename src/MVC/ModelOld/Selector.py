from PyAsoka.Debug import Logs
from PyAsoka.src.MVC.ModelOld.Field import ReferenceField


class Selector:
    def __init__(self, _type):
        self.type = _type
        self.database = _type.conf.database
        self.table = _type.conf.table
        self.private = _type.fields
        self.references = _type.references
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

    def fields(self):
        return {**self.private, **self.references}

    def clear(self):
        self._where_ = {}
        self._limit_ = None
        self._offset_ = None

    def __add_compare__(self, key, arg, _type):
        field = self.fields()[key]
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
            field = self.fields()[key]
            if field is not None:
                cols += key + ', '
                vals += f'?, '
                params.append(value)
        cols, vals = cols[:len(cols) - 2], vals[:len(vals) - 2]
        self.database.connect(self.table.profile)
        if self.database.execute(f'INSERT INTO {self.table.name} ({cols}) VALUES ({vals});', list(params)):
            self.clear()
            _id = self.database.getLastAutoincrement(self.table.name)
            return self.type.containerType(id=_id, **kwargs)
            # return self.filter(id=_id).get()
        else:
            return False

    def get(self, *args):
        data = self.getDict(*args)
        args = {}
        if data:
            for row in data:
                for key, arg in row.items():
                    field = self.fields()[key]
                    if isinstance(field, ReferenceField):
                        args[key] = int(arg)
                    else:
                        args[key] = field.fromSql(arg)
            objects = self.type.containerType(**args)
            return objects
        else:
            return None

    def getDict(self, *args):
        where, where_vals = self.__where__()
        limit = self.__limit__()

        if len(args) == 0:
            keys, all_keys = '', True
            for field in self.fields().values():
                # if field.autoload:  ToDo
                keys += field.column.name + ', '
                # else:
                #    all_keys = False
            if all_keys:
                keys = '*'
            elif len(keys) > 0:
                keys = keys[:len(keys) - 2]
        else:
            keys = ''
            for key in args:
                fld = self.fields()[key]
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
            fld = self.fields()[key]
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
