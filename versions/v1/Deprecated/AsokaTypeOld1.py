import os
import json
import PyAsoka.Asoka as asoka
from PyAsoka.Instruments import Log
from PyAsoka.Database.SqLite import SqLite as Database


class FieldType:
    int = 1
    bool = 2
    string = 3
    blob = 4
    array = 5
    dictionary = 6
    object = 7
    objects_array = 8

    @staticmethod
    def toSqlType(type):
        dic = {
            FieldType.int: 'INTEGER',
            FieldType.bool: 'BOOLEAN',
            FieldType.string: "TEXT",
            FieldType.blob: 'BLOB',
            FieldType.array: 'TEXT',
            FieldType.dictionary: 'TEXT',
            FieldType.object: 'TEXT'
        }
        return dic.get(type)


class Structure:

    def __init__(self):
        self.map = {}

    def create_field(self, name, type, value=None, length=asoka.nullInt):
        if type is FieldType.objects_array and value is None:
            value = []
        self.map[name] = {
            'type': type,
            'value': value
        }
        if length is not asoka.nullInt:
            self.map['name']['length'] = length
        return self

    def getMap(self):
        return self.map


def databaseConfig(location, table, type='sqlite'):
    return {
        'location': location,
        'table': table,
        'type': type
    }


def environmentConfig(file):
    return {
        'file': os.path.basename(file).rstrip('.py')
    }


class AsokaTypeOld:

    def __init__(self, id = asoka.nullInt, structure = None, database = None, environment = None):
        self.structure = structure
        self.structure['id'] = {'type': FieldType.int, 'value': id}
        self.database = database
        self.environment = environment
        if not self.tableExist():
            self.createTable()

    def getGenerator(self):
        file = self.environment.get('file')
        class_name = self.__class__.__name__
        code = f"from {file} import {class_name} \n" \
               f"new_obj = {class_name}()"
        return code

    def tableExist(self):
        if not self.__database_is_ok__():
            Log.warning("Type.checkTable(): обращение к SQL с некорректными параметрами")
            return False

        db_type = self.database.get('type')
        if db_type == 'sqlite':
            Database.init(self.database.get('location'))

        for table in Database.getTableNames():
            if table.get('name') == self.database.get('table'):
                return True
        return False

    def createTable(self):
        if not self.__database_is_ok__():
            Log.warning("Type.createTable(): обращение к SQL с некорректными параметрами")
            return

        fields = 'id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, '
        for key in self.structure.keys():
            if key != 'id':
                sql_type = None
                type = self.structure[key].get('type')
                sql_type = FieldType.toSqlType(type)
                fields += f'{key} {sql_type}'
                if mod := self.structure[key].get('modifier') is not None:
                    fields += ' ' + mod()
                fields += ', '
        fields = fields.rstrip(', ')

        db_type = self.database.get('type')
        if db_type == 'sqlite':
            Database.init(self.database.get('location'))

        table = self.database.get('table')
        query = f"CREATE TABLE IF NOT EXISTS {table} ({fields});"
        Database.execute(query)

    def getId(self):
        id = self.get('id')
        if id is None:
            return asoka.nullInt
        else:
            return id

    def setId(self, id):
        self.set('id', id)

    def set(self, name, value):
        self.structure[name]['value'] = value

    def get(self, name):
        result = self.structure.get(name).get('value')
        if name != 'id' and result is None and self.__database_is_ok__():
            result = self.loadField(name)
        return result

    def load(self, id = asoka.nullInt):
        if not self.__database_is_ok__():
            Log.warning("Type.load(): обращение к SQL с некорректными параметрами")
            return

        if id == asoka.nullInt:
            id = self.get('id')
        else:
            self.set('id', id)
        table = self.database.get('table')
        db_type = self.database.get('type')

        if db_type == 'sqlite':
            Database.init(self.database.get('location'))

        query = f"SELECT * FROM {table} WHERE id = {id};"
        data = Database.query(query)
        if len(data) != 0:
            data = data[0]
            if self.database.get('type') == 'sqlite':
                for key in self.structure.keys():
                    self.__fromSQL__(key, data)
        else:
            Log.error("Type.load(): пустой результат SQL запроса")

    def loadField(self, name):
        if not self.__database_is_ok__():
            Log.warning("Type.loadField(): обращение к SQL с некорректными параметрами")
            return
        if self.structure.get(name) is None:
            return None

        db_type = self.database.get('type')
        if db_type == 'sqlite':
            Database.init(self.database.get('location'))

        query = f"SELECT {name} FROM {self.database.get('table')} WHERE id = {self.getId()};"
        data = Database.query(query)
        try:
            self.__fromSQL__(name, data[0])
            return self.structure[name]['value']
        except Exception:
            Log.error("Type.loadField(): ошибка получения данных")
            return None

    def save(self):
        if self.__exist__():
            self.update()
        else:
            self.insert()

    def insert(self):
        if not self.__database_is_ok__():
            Log.warning("Type.insert(): обращение к SQL с некорректными параметрами")
            return
        table = self.database.get('table')
        fields = ""
        args = ""
        structure = self.structure.copy()
        structure.pop('id')

        for key in structure.keys():
            fields += key + ', '
            field_value = self.__toSQL__(key)
            args += field_value + ", "
        fields = fields.rstrip(", ")
        args = args.rstrip(", ")

        db_type = self.database.get('type')
        if db_type == 'sqlite':
            Database.init(self.database.get('location'))

        query = f"INSERT INTO {table} ({fields}) VALUES({args});"

        if db_type == 'sqlite':
            Database.execute(query, save_row_id=True)
            self.set('id', Database.lastRowId)
        elif db_type == 'mysql':
            data = Database.query(f"SELECT MAX('id') FROM {table};")
            try:
                if db_type == 'mysql':
                    print(data[0])
                    self.set('id', data[0]['id'])
            except Exception:
                Log.error(f"Type.insert(): {table}: Не удалось получить id")

    def update(self):
        if not self.__database_is_ok__():
            Log.warning("Type.update(): обращение к SQL с некорректными параметрами")
            return
        table = self.database.get('table')
        id = self.get('id')
        args = ""
        structure = self.structure.copy()
        structure.pop('id')

        for key in structure.keys():
            field_type = structure.get(key).get('type')
            if field_type is None:
                Log.error('Type.update(): поле класса имеет тип None')
                return

            field_value = self.__toSQL__(key)

            args += f"{key} = {field_value}, "
        args = args.rstrip(", ")

        db_type = self.database.get('type')
        if db_type == 'sqlite':
            Database.init(self.database.get('location'))

        query = f"UPDATE {table} SET {args} WHERE id = {id};"
        Database.execute(query)

    def remove(self):
        if not self.__database_is_ok__():
            Log.warning("Type.remove(): обращение к SQL с некорректными параметрами")
            return
        if self.getId() == asoka.nullInt:
            Log.warning("Type.remove(): невозможно выполнить с неактуальным id")
            return

        for key in self.structure:
            if self.structure.get(key).get('type') is FieldType.object:
                if obj := self.get(key) is not None:
                    obj.remove()

        table = self.database.get('table')
        query = f"DELETE FROM {table} WHERE id = {self.getId()};"
        Database.execute(query)

    def __exist__(self):
        if not self.__database_is_ok__():
            Log.warning("Type.load(): обращение к SQL с некорректными параметрами")
            return
        table = self.database.get('table')
        id = self.get('id')
        if id == asoka.nullInt:
            return False
        query = f"SELECT id FROM {table} WHERE id = {id};"
        data = Database.query(query)
        if len(data) == 0:
            return False
        else:
            return True

    def __fromSQL__(self, name, data):
        value = data.get(name)
        type = self.structure[name]['type']

        if type is FieldType.int:
            value = int(value)
        elif type is FieldType.bool:
            value = bool(value)
        elif type in (FieldType.array, FieldType.dictionary):
            value = json.loads(value)
        elif type is FieldType.object:
            data = json.loads(value)
            id = data.get('id')
            generator = data.get('generator')
            local = {'new_obj': None}
            exec(generator, local, local)
            value = local.get('new_obj')
            value.setId(id)
        elif type is FieldType.objects_array:
            data = json.loads(value)
            ids = data.get('ids')
            generator = data.get('generator')
            value = []
            if generator != '':
                for id in ids:
                    local = {'new_obj': None}
                    exec(generator, local, local)
                    obj = local.get('new_obj')
                    obj.setId(id)
                    value.append(obj)

        self.structure[name]['value'] = value

    def __toSQL__(self, name):
        value = self.structure.get(name).get('value')
        type = self.structure.get(name).get('type')
        if value is None:
            if type is FieldType.int:
                value = '0'
            elif type is FieldType.bool:
                value = 'False'
            elif type in (FieldType.string,  FieldType.blob):
                value = ''
            elif type in (FieldType.array, FieldType.dictionary, FieldType.object):
                value = ''
        else:
            if type in (FieldType.int, FieldType.bool):
                value = str(value)
            elif type in (FieldType.string, FieldType.blob):
                value = f'"{value}"'
            elif type in (FieldType.array, FieldType.dictionary):
                value = f'"{json.dumps(value)}"'
            elif type is FieldType.object:
                print(f'Сохраняю объект')
                value.save()
                value = json.dumps({
                    'id': value.getId(),
                    'generator': value.getGenerator()
                })
                value = f"'{value}'"
            elif type is FieldType.objects_array:
                ids = []
                generator = value[0].getGenerator() if len(value) else ''
                for obj in value:
                    obj.save()
                    ids.append(obj.getId())
                value = json.dumps({
                    'ids': ids,
                    'generator': generator
                })
                value = f"'{value}'"

        return value

    def __database_is_ok__(self):
        if self.database is None or self.database.get('type') is None or self.database.get('location') is None or self.database.get('table') is None:
            return False
        else:
            return True
