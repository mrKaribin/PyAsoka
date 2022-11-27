from PyAsoka.Database.ADatabaseProfile import *
from PyAsoka.Instruments.Log import *
import json


class DbField:
    def __init__(self, autoload: bool = False, autoupdate: bool = False):
        self.autoload = autoload
        self.autoupdate = autoupdate
        self.keys = {}
        self.reference = False
        self.list_reference = False

    def primary_key(self):
        self.keys[a.types.db.constraints.PRIMARY_KEY] = True
        return self

    def foreign_key(self, table: str, field: str):
        self.keys[a.types.db.constraints.FOREIGN_KEY] = (table, field)
        return self

    def autoincrement(self):
        self.keys[a.types.db.constraints.AUTOINCREMENT] = True
        return self

    def unique(self):
        self.keys[a.types.db.constraints.UNIQUE] = True
        return self

    def not_null(self):
        self.keys[a.types.db.constraints.NOT_NULL] = True
        return self

    def default(self, value):
        self.keys[a.types.db.constraints.DEFAULT] = value
        return self

    def get_advt(self, name, datatype, lang=a.types.db.lang.sqlite):
        l = a.types.db.lang
        if lang == l.sqlite:
            from PyAsoka.Database.SqLite import SqLite as db
            result = f'{name} {db.toSqlType(datatype)} '
            for key in self.keys.keys():
                result += db.getConstraint(key, self.keys[key])
            return result

    def set_reference(self, obj, field: str = 'id', name: str = False):
        if issubclass(obj, AType):
            obj = obj.classname
        elif not isinstance(obj, str):
            error(f'DbField::set_reference: Неверно указана внешняя зависимость')
        self.reference = (obj, field, name)
        return self

    def set_list_reference(self, obj, field: str = 'id', name: str = False):
        if issubclass(obj, AType):
            obj = obj.classname
        elif not isinstance(obj, str):
            error(f'DbField::set_list_reference: Неверно указана внешняя зависимость')
        self.list_reference = (obj, field, name)
        return self


class Field:
    def __init__(self, name: str = None, datatype: str = None, access: tuple = (False, False), regular: str = None, dbfield: DbField = False):
        self.name = name
        self.datatype = datatype
        self.access = access
        self.regular = regular
        self.dbfield = dbfield


class NetProfile:
    def __init__(self):
        pass


class Mode:
    def __init__(self, database_profile: ADatabaseProfile = False, net_profile: NetProfile = False):
        self.database = database_profile
        self.network = net_profile


class AType:
    inheritors = {}


def generate_imports():
    return f"""
import json
import asoka as a
from Service.Log import *
from Database.SqLite import SqLite as Database
from Types.alist import *
from copy import *
"""


def generate_init(classname, fields, structure, names, functions):
    func_name = '__init__'
    params = ''
    for fld in fields:
        datatype = f': {fld.datatype}' if fld.datatype in a.types.compile else ''
        default = f"eval('{fld.datatype}()')" if fld.datatype in a.types.compile else 'None'
        params += f', {fld.name}' + datatype + ' = ' + default
    code = f"""
def {func_name}(self{params}):
"""

    for fld in fields:
        name = f'__{fld.name}__' if True in fld.access else fld.name
        if fld.access[1]:
            value = 'None'
            init = f'self.set_{fld.name}({fld.name})'
        else:
            value = f'{fld.name}'
            init = f'''comment('{classname}.__init__: Записываю в поле {fld.name} значением %s (%s)' % (self.{name}, type(self.{name})))'''
        names[fld.name] = name
        structure[f'_{fld.name}_'] = fld
        code += f"""
    self.{name} = {value}
    {init}
"""

        get, set = fld.access
        if get:
            functions.update(generate_getter(fld))
        if set:
            functions.update(generate_setter(fld, classname))

    code += f"""
    self.__check_table__()
"""
    functions[func_name] = code

    func_name = 'from_id'
    code = f"""
@staticmethod
def {func_name}(id):
    object = {classname}()
    object.set_id(id)
    return object.load()
"""
    # functions[func_name] = code


def generate_getter(fld):
    func_name = f'get_{fld.name}'
    field_name = f'__{fld.name}__' if True in fld.access else fld.name
    return {func_name: f"""
def {func_name}(self{', load=False' if fld.dbfield != False else ''}):
    return {f'copy(self.{field_name})' if fld.datatype in a.types.composite else f'self.{field_name}'}
"""}


def generate_setter(fld, classname):
    fnc_name = f'set_{fld.name}'
    field_name = f'__{fld.name}__' if True in fld.access else fld.name

    if fld.datatype != a.types.runnable and fld.datatype in a.types.all:
        condition = f'isinstance(value, {fld.datatype})'
    elif fld.datatype == a.types.runnable:
        condition = f'callable(value)'
    elif fld.datatype in [classname] + list(AType.inheritors.keys()):
        condition = f'isinstance(value, AType) and value.classname == "{fld.datatype}"'
    else:
        condition = f'True'

    return {fnc_name: f"""
def {fnc_name}(self, value{', save=False' if fld.dbfield != False else ''}):
    if {condition}:
        self.{field_name} = value
        comment('%s.{fnc_name}: Записываю в поле {fld.name} значение %s' % (self.classname, value))
    else:
        warning('%s.{fnc_name}: Попытка записи поля {fld.name} неверным типом данных <%s>' % (self.classname, type(value)))
"""}


def generate_to_json():
    pass


def generate_service():
    result = {}

    return result


def generate_database_service(db_mode):
    result = {}

    func_name = 'getDbFields'
    result[func_name] = f"""
def {func_name}(self, names:tuple=False):
    result = {'{}'}
    if names is False:
        names = self.__fields__.keys()
    for key in names:
        field = eval('self._%s_' % key)
        if field.dbfield is not False:
            field = copy(field)
            value = eval('self.%s' % self.__fields__[key]) 
            result[key] = (field, value)
    return result
"""

    func_name = '__check_table__'
    result[func_name] = f"""
def {func_name}(self):
    if not self.__database_is_ok__():
        warning("%s.exist: Некорректные параметры базы данных" % cls.classname)
        return
        
    from Database.{db_mode.lang} import {db_mode.lang} as db
    db.init(self.__mode__.database)
    for table in db.getTables():
        if table.get('name') == self.__mode__.database.table:
            return
    self.__table_create__()
"""

    func_name = '__table_create__'
    result[func_name] = f"""
def {func_name}(self):
    if not self.__database_is_ok__():
        warning("%s.{func_name}: обращение к SQL с некорректными параметрами" % (self.classname))
        return
    
    from Database.{db_mode.lang} import {db_mode.lang} as db
    fields = ''
    for field in self.__fields__:
        info = eval('self._%s_' % field)
        fields += info.dbfield.get_advt(field, info.datatype, self.__mode__.database.lang) + ', '
    fields = fields[:len(fields) - 3]
    query = 'CREATE TABLE IF NOT EXISTS %s (%s)' % (self.__mode__.database.table, fields)
    db.init(self.__mode__.database)
    db.execute(query)
"""

    func_name = '__database_is_ok__'
    result[func_name] = f"""
@classmethod
def {func_name}(cls):
    return True
"""

    func_name = 'exist'
    result[func_name] = f"""
@classmethod
def {func_name}(cls, id):
    if not cls.__database_is_ok__():
        warning("%s.exist: Некорректные параметры базы данных" % cls.classname)
        return
        
    from Database.{db_mode.lang} import {db_mode.lang} as Database
    table = cls.__mode__.database.table
    if id < 1:
        return False
    query = 'SELECT id FROM %s WHERE id = %s;' % (table, id)
    data = Database.query(query)
    if len(data) == 0:
        return False
    else:
        return True
"""

    func_name = 'existSelf'
    result[func_name] = f"""
def {func_name}(self):
    return self.exist(self.get_id(True))
"""

    func_name = 'save'
    result[func_name] = f"""
def {func_name}(self, names: tuple = False):
    if self.existSelf():
        if names is False:
            self.update()
        else:
            self.update_self(self.getDbFields(names))
    else:
        if names is False:
            self.insert()
        else:
            self.insert_with(self.getDbFields(names))
"""

    return result


def generate_reference(field):
    obj, fld, name = field.dbfield.reference
    func_name = f'{obj.lower() if not name else name}'
    call = f'self.get_{field.name}()' if field.access[0] else f'self.__{field.name}__' if True in field.access else f'self.{field.name}'
    code = f"""
def {func_name}(self):
    return AType.inheritors['{obj}']({fld}={call}).load()
"""
    return {func_name: code}


def generate_list_reference(field, dbmode, classname):
    obj, fld, name = field.dbfield.list_reference
    func_name = f'getListFor{obj}' if not name else name
    code = f"""
@staticmethod
def {func_name}(obj):
    if isinstance(obj, AType.inheritors[{obj}]):
        _id = obj.get_id()
    elif isinstance(obj, int):
        _id = obj
    else:
        error('{classname}::{func_name}: Получены некорректные данные')
        return []
    from Database.{dbmode.lang} import {dbmode.lang} as db
        
    query = 'SELECT {fld} FROM {dbmode.table} WHERE {field.name} = %s' % _id
    data = db.query(query)
    result = []
    for row in data:
        if len(row):
            AType.inheritors[{obj}]({fld}=row[0]).load()
    return result
"""
    return {func_name: code}


def quotes(string):
    return f"'{string}'"


@classmethod
def to_sql(cls, value, datatype):
    if value is not None and value.__class__.__name__ != datatype:
        raise Exception(f'Значение типа <{type(value)}> не соответствует заявленному типу <{datatype}>')
    if value is None:
        return "'NULL'"
    t = a.types

    if datatype in (t.int, t.bool, t.float):
        return str(value)

    elif datatype in (t.str, t.bytes):
        return quotes(str(value))

    elif datatype in (t.tuple, t.list, t.dict):
        try:
            return f"'{json.dumps(value)}'"
        except Exception:
            warning(f'{cls.classname}:to_sql(): Некорректные данные. '
                    f'Значение типа <{type(value)}> невозможно преобразовать в JSON')
            return {} if datatype == t.dict else []

    elif datatype == a.types.alist:
        result = {}
        last_type = None
        same_type = True
        for obj in value:
            if obj.__class__.__name__ != AType:
                if last_type is not None and last_type != type(obj):
                    same_type = False
                else:
                    last_type = type(obj)
                if obj.classname is not cls.classname:
                    obj.save()
                result[obj.get_id()] = type(obj)
            else:
                raise Exception(f'Некорректные данные. Значение типа <{type(obj)}> в объекте <alist>')
        if same_type:
            return "''"
        else:
            return json.dumps(result)

    elif isinstance(value, AType):
        # if value.classname is not cls.classname:
        # value.save()
        if (value_id := value.get_id()) is not None:
            return str(value_id)
        else:
            raise Exception(f'Не удалось получить корректный id класса <{value.classname}>')


def from_sql(self, value, datatype):
    # for field in eval(datatype).__fields__:
    #         fld = eval(f'{datatype}.__{field}__')
    #         db_mode = self.__mode__.database
    #         for key in fld.dbfield.keys:
    #             if key[0] == a.types.db.constraints.FOREIGN_KEY and key[1] == db_mode.table and key[2] == 'id':
    #                 eval()
    pass


def generate_insert(db_mode):
    result = {}
    func_name = 'insert_with'
    code = f"""
@classmethod
def {func_name}(cls, data:dict):
    # comment(data)
    from Database.{db_mode.lang} import {db_mode.lang} as db
    names = ''
    values = ''

    for key in data.keys():
        try:
            field, value = data[key]
            values += cls.to_sql(value, field.datatype) + ', '
            names += key + ', '
        except Exception as e:
            warning(f'%s.{func_name}(): Ошибка при обработке значения %s: %s' % (cls.classname, key, str(e)))

    names = names[0:len(names) - 2]
    values = values[0:len(values) - 2]

    query = 'INSERT INTO {db_mode.table} (%s) VALUES (%s);' % (names, values)
    db.init(cls.__mode__.database)
"""
    if db_mode.lang == a.types.db.lang.sqlite:
        code += f"""
    db.execute(query, True)
    return db.lastRowId
"""
    result[func_name] = code

    func_name = 'insert'
    result[func_name] = f"""
def {func_name}(self, names: tuple = False):
    data = self.getDbFields() if names is False else self.getDbFields(names)
    data.pop('id', None)
    id = self.insert_with(data)
    self.set_id(id)
"""
    return result


def generate_update(db_mode):
    result = {}
    func_name = 'update_with'
    code = f"""
@classmethod
def {func_name}(cls, data:dict, where:str=None):
    from Database.{db_mode.lang} import {db_mode.lang} as db
    changes = ''

    for key in data.keys():
        try:
            field, value = data[key]
            value = cls.to_sql(value, field.datatype)
            changes += '%s = %s, ' % (key, value)
        except Exception as e:
            warning(f'%s.{func_name}(): Ошибка при обработке значения %s: %s' % (cls.classname, key, str(e)))

    changes = changes[0:len(changes) - 2]

    query = 'UPDATE {db_mode.table} SET %s ' % changes
    if where is not None:
        query += ' WHERE %s' % where
    query += ' ;'
    db.init(cls.__mode__.database)
    data = db.execute(query)
"""
    result[func_name] = code

    func_name = 'update'
    result[func_name] = f"""
def {func_name}(self, names: tuple = False):
    data = self.getDbFields() if names is False else self.getDbFields(names)
    data.pop('id', None)
    id = self.update_with(data, 'id = %d' % self.get_id())
    # self.setId(id)
"""
    return result


def generate_select(db_mode):
    result = {}
    func_name = 'select_with'
    code = f"""
@classmethod
def {func_name}(cls, data:list=None, where:str=None):
    from Database.{db_mode.lang} import {db_mode.lang} as db
    if data is None:
        fields = '*'
    else:
        fields = ''
        for field in data:
            fields += field + ', '
        fields = fields[:len(fields)-2]
    
    query = 'SELECT %s FROM {db_mode.table}' % fields
    if where is not None:
        query += ' WHERE ' + where
    query += ' ;'
    db.init(cls.__mode__.database)
    return db.query(query)
"""
    result[func_name] = code

    func_name = 'load'
    code = f"""
def {func_name}(self, data: list = None):
    id = self.get_id()
    if len(selected := self.select_with(data, where='id = %s' % id)):
        self.from_dict(selected[0])
        if data is None:
            comment('%s.{func_name}: Загружены из БД данные об объекте (id = %s)' % (self.classname, id))
    else:
        warning('%s.{func_name}: Не удалось загрузить из БД данные об объекте (id = %s)' % (self.classname, id))
    return self
"""
    result[func_name] = code

    func_name = 'find'
    code = f"""
@classmethod
def {func_name}(cls, where: str):
    results = []
    for row in self.select_with((id), where=where):
        if (id := row['id']) is not None:
            results.append(eval('%s(id=id).load()' % self.classname))
    # warning('%s.{func_name}: Не удалось загрузить из БД данные по запросу %s' % (self.classname, where))
    return results
"""
    result[func_name] = code

    return result


def generate_remove(lang=a.types.db.lang.sqlite):
    pass


def generate_json(fields):
    result = {}
    func_name = 'from_dict'
    code = f"""
def {func_name}(self, data: dict):
    for key in data.keys():
        for field_name in self.__fields__:
            field = eval('self._%s_' % field_name)
            if key == field.name:
                # print(field.datatype, data[key])
                if field.datatype in {a.types.simple}:
                    if isinstance(data[key], eval(field.datatype)):
                        value = data[key]
                    elif isinstance(data[key], str):
                        value = eval('%s("%s")' % (field.datatype, data[key]))
                    elif isinstance(data[key], int):
                        value = eval('%s(%s)' % (field.datatype, data[key]))
                elif field.datatype in {a.types.containers}:
                    value = json.loads(data[key])
                elif field.datatype in AType.inheritors.keys() and (isinstance(data[key], str) or isinstance(data[key], int)):
                    if isinstance(data[key], int) or data[key].isdigit():
                        atype = AType.inheritors[field.datatype]
                        value = atype(id=int(data[key]))
                        if value.classname != self.classname:
                            value.load()
                    else:
                        value = data[key].from_json()
                else:
                    value = data[key]
                
                if field.access[1]:
                    eval('self.set_%s' % field.name)(value)
                elif True in field.access:
                    exec('self.__%s__ = value' % field.name, {{'value': value, 'self': self}})
                    comment('%s.{func_name}: Записываю в поле %s значение %s' % (self.classname, field_name, value))
                else:
                    exec('self.%s = value' % field.name, {{'value': value, 'self': self}})
                    comment('%s.{func_name}: Записываю в поле %s значение %s' % (self.classname, field_name, value))
"""
    result[func_name] = code

    return result


def create_class(classname, parents=(), fields=(), mode: Mode = False):
    if (atype := AType.inheritors.get(classname)) is not None:
        warning(f'AType: Попытка повторно объявить тип {classname}')
        return atype

    comment(f'Создаю класс {classname}:', True)
    structure = {}
    fields_names = {}
    functions = {}
    fields = [Field('id', a.types.int, (True, True), dbfield=DbField().primary_key().autoincrement())] + list(fields)
    parents = ('AType', ) + parents

    atypes = [classname] + list(AType.inheritors.keys())
    for field in fields:
        if field.dbfield and field.datatype in atypes:
            if field.datatype != classname:
                table = AType.inheritors[field.datatype].__mode__.database.table
            else:
                table = mode.database.table
            field.dbfield.foreign_key(table, 'id')

        if field.dbfield.reference is not False or field.dbfield.list_reference is not False:
            ref = field.dbfield.reference if field.dbfield.reference else field.dbfield.list_reference
            obj, fld, name = ref
            if field.datatype != classname:
                table = AType.inheritors[obj].__mode__.database.table
            else:
                table = mode.database.table
            field.dbfield.foreign_key(table, fld)
            functions.update(generate_reference(field))
            if field.dbfield.list_reference is not False:
                functions.update(generate_list_reference(field, mode.database, classname))

    # Добавляем в структуру поля будущего класса
    generate_init(classname, fields, structure, fields_names, functions)

    # Создаем код методов
    functions.update(generate_service())
    if mode.database is not False:
        db_mode = mode.database
        structure['to_sql'] = to_sql
        structure['from_sql'] = from_sql
        functions.update(generate_database_service(db_mode))
        functions.update(generate_insert(db_mode))
        functions.update(generate_update(db_mode))
        functions.update(generate_select(db_mode))
        functions.update(generate_json(fields))

    # Добавляем в структуру методы будущего класса
    exec(generate_imports())
    for key in functions.keys():
        comment(f'Объявляю метод {key}(?)')
        exec(functions[key])
        structure[key] = eval(key)

    # Добавляем статические поля и методы
    structure['__fields__'] = fields_names      # Хранит все имена переменных класса
    structure['__mode__'] = mode                # Хранит настройки автоматизации работы с данными
    structure['classname'] = classname          # Хранит имя класса
    structure['atype'] = True                   # Флаг принадлежности к AType

    inheritance = ''
    if parents is not None and len(parents) > 1:
        for parent in parents:
            inheritance += f'{parent}, '
        inheritance = f'({inheritance[0:len(inheritance) - 2]})'
    else:
        inheritance = f'({parents[0]}, )'

    new_type = type(classname, eval(inheritance), structure)
    AType.inheritors[classname] = new_type
    return new_type
