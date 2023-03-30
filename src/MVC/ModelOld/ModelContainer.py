from PyAsoka.src.Database.DatabaseProfile import DatabaseProfile, DatabaseType
from PyAsoka.src.MVC.ModelOld.ObjectField import ObjectField, ObjectReference


class ModelContainer(object):
    _fields_ = {}
    _references_ = {}

    model = None
    database = DatabaseProfile(DatabaseType.SQLITE, 'tests.db', 'root', '').getDriver()
    table = database.Table(database.profile, 'Default')

    def __init__(self, **kwargs):
        self.exist_in_database = False
        self.fields = {}
        self.references = {}
        self.updated = True
        for field in self._fields_.values():
            name = field.column.name
            if name in kwargs.keys():
                value = kwargs[name]
            else:
                value = None
            attr = ObjectField(self, field, value)

            setattr(self.__class__, name, property(attr.get, attr.set))
            self.fields[field.name] = attr

        for reference in self._references_.values():
            name = reference.name
            value = kwargs[name] if name in kwargs.keys() else None
            id_name = reference.column.name
            value_id = kwargs[id_name] if id_name in kwargs.keys() else None
            attr = ObjectReference(self, reference, value, value_id)

            setattr(self.__class__, name, property(attr.get, attr.set))
            setattr(self.__class__, id_name, property(attr.getId, attr.setId))
            self.references[reference.column.name] = attr

    def __str__(self):
        return self.print()

    def print(self, indent_size=0):
        indent = ''
        for i in range(indent_size):
            indent += ' '
        result = f'\n{indent}class {self.__class__.__name__} || id: {self.fields["id"].value}'
        for field in {**self.fields, **self.references}.values():
            result += f'\n    {indent}({type(field.value)}) {field.column.name}: ' \
                      f'{field() if not issubclass(field._type_, ModelContainer) else field().print(indent_size + 4)}'
        return result

    def insert(self):
        args = {}
        for field in self.fields.values():
            if field.value is not None and field.column.name != 'id':
                args[field.column.name] = field.value

        for field in self.references.values():
            if field.id is not None:
                args[field.column.name] = field.id
                if issubclass(type(field.value), ModelContainer):
                    field.value.save()

        obj = self.model.objects().create(**args)
        if obj:
            self.id = obj.id
            self.exist_in_database = True
            self.updated = False
            return self
        else:
            raise Exception('Ошибка при получении идентификатора новой строки таблицы')

    def update(self):
        args = {}
        for field in self.fields.values():
            if field.value is not None and field.column.name != 'id':
                args[field.column.name] = field.value

        for field in self.references.values():
            if field.id is not None:
                args[field.column.name] = field.id
                if issubclass(type(field.value), ModelContainer):
                    field.value.save()
        self.model.objects().filter(id=self.id).set(**args)
        self.exist_in_database = True
        self.updated = False
        return self

    def exists(self):
        if not self.exist_in_database:
            self.exist_in_database = self.model.objects().filter(id=self.id).exists()
        return self.exist_in_database

    def save(self):
        if self.updated:
            if self.id is not None and self.exists():
                self.update()
            else:
                self.insert()
        return self

    def load(self):
        data = self.model.objects().filter(id=self.id).getDict()
        if data:
            data = data[0]
            for key, value in data.items():
                field = {**self.fields, **self.references}[key]
                if field is not None:
                    field.value = self._fields_[key].fromSql(value)
        return self

    def delete(self):
        self.model.objects().filter(id=self.id).delete()
        return self
