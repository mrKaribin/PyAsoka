from PyAsoka.src.Core.Object import Object, ObjectMeta
from PyAsoka.Asoka import Asoka

from PyAsoka.src.MVC.Model.ModelScheme import ModelScheme
from PyAsoka.src.MVC.Model.Field import Field, SimpleField, Reference, OneToOne, ManyToOne, OneToMany, ManyToMany, \
    ManyToManyField, IntField, BoolField, StrField, FloatField, BinaryField
from PyAsoka.src.MVC.Model.ObjectField import ObjectField, ObjectOneToOne, ObjectOneToMany, ObjectManyToMany
from PyAsoka.src.MVC.Model.ObjectReference import ObjectReference
from PyAsoka.src.MVC.Model.Selector import Selector


class ModelMeta(ObjectMeta):
    newId = 0
    models = {}

    def __new__(mcs, name, bases, attrs: dict, profile=None, table_name=None):
        profile = profile if profile is not None else Asoka.Databases.asoka
        tableName = table_name if table_name is not None else name
        scheme = ModelScheme(profile, tableName)
        fields = {}
        mto_fields = {}
        mtm_fields = {}
        ModelMeta.newId += 1

        attrs['id'] = IntField().PRIMARY_KEY().UNIQUE().NOT_NULL()
        for key in list(attrs.keys()):
            attr = attrs[key]
            if isinstance(attr, Field):
                attr.name = key
                attr.column = attr.toColumn(profile.type)
                fields[key] = attr
                scheme.table.columns.append(attr.column)
                scheme.fields[key] = attr
                if isinstance(attr, SimpleField):
                    scheme.simpleFields[key] = attr
                if isinstance(attr, OneToOne):
                    scheme.references[key] = attr
                    scheme.table.add(attr.toReference(profile.type))
                if isinstance(attr, ManyToOne):
                    mto_fields[key] = attr

            if isinstance(attr, ManyToMany):
                mtm_fields[key] = attr
                attrs.pop(key)

        scheme.database.connect(scheme.profile)
        if len(fields) > 1 and not scheme.table.isExist():
            scheme.table.create()

        attrs['_fields_'] = fields
        attrs['classId'] = -1
        attrs['scheme'] = scheme
        cls = super().__new__(mcs, name, bases, attrs)

        for key, field in mto_fields.items():
            if field.listname is None:
                field.listname = name[0].lower() + name[1:] + 'List'
            field.model._fields_[field.listname] = OneToMany(cls, field.column)

        for key, field in mtm_fields.items():
            fld, fld2 = field.create(cls)
            if field.listname is None:
                field.listname = name[0].lower() + name[1:]
            field.model1._fields_[key] = fld
            field.model2._fields_[field.listname] = fld2

        ModelMeta.models[ModelMeta.newId] = ModelMeta
        cls.classId = ModelMeta.newId

        return cls


class ModelPrototype(Object, metaclass=ModelMeta):

    @classmethod
    @property
    def selector(cls) -> Selector:
        return Selector(cls)


class Model(ModelPrototype):
    IntField = IntField
    BoolField = BoolField
    FloatField = FloatField
    StrField = StrField
    BinaryField = BinaryField

    def __init__(self, **kwargs):
        super().__init__()
        self.exist_in_database = False
        self.updated = False
        scheme = ModelScheme(self.scheme.profile, self.scheme.table.name)
        scheme.table = self.scheme.table

        for key, field in self._fields_.items():
            if isinstance(field, SimpleField):
                new_fld = ObjectField(self, field)
                scheme.fields[key] = new_fld
                scheme.simpleFields[key] = new_fld
                setattr(self.__class__, key, property(
                    lambda inst, name=key: inst.scheme.fields[name].getter(),
                    lambda inst, value, name=key: inst.scheme.fields[name].setter(value)
                ))
                if key in kwargs.keys():
                    new_fld.setter(kwargs[key])

            elif isinstance(field, OneToOne):
                new_ref = ObjectOneToOne(self, field)
                scheme.fields[key] = new_ref
                scheme.references[key] = new_ref
                setattr(self.__class__, key + 'Id', property(
                    lambda inst, name=key: inst.scheme.fields[name].idGetter(),
                    lambda inst, value, name=key: inst.scheme.fields[name].idSetter(value)
                ))
                setattr(self.__class__, key, property(
                    lambda inst, name=key: inst.scheme.fields[name].valueGetter(),
                    lambda inst, value, name=key: inst.scheme.fields[name].valueSetter(value)
                ))
                if key in kwargs.keys():
                    new_ref.valueSetter(kwargs[key])
                if key + 'Id' in kwargs.keys():
                    new_ref.idSetter(kwargs[key + 'Id'])

            elif isinstance(field, OneToMany):
                new_otm = ObjectOneToMany(self, field)
                scheme.OTM_refs[key] = new_otm
                setattr(self, key, new_otm.getter)

            elif isinstance(field, ManyToManyField):
                new_mtm = ObjectManyToMany(self, field)
                scheme.MTM_refs[key] = new_mtm
                setattr(self, key + 'List', new_mtm.getter)
                setattr(self, 'add' + key[0].upper() + key[1:], new_mtm.add)
        self.scheme = scheme

    def __str__(self):
        return self.print()

    def print(self, indent_size=0):
        indent = ''
        for i in range(indent_size):
            indent += ' '
        result = f'\n{indent}class {self.__class__.__name__} || id: {self.scheme.fields["id"].value}'
        for field in {**self.scheme.simpleFields, **self.scheme.references}.values():
            result += f'\n    {indent}({field.type}) {field.column.name}: ' \
                      f'{field.value if not isinstance(field, ObjectOneToOne) else field.valueGetter().print(indent_size + 4)}'
        return result + '\n'

    def insert(self):
        args = {}
        for field in self.scheme.simpleFields.values():
            if isinstance(field, ObjectField) and field.value is not None and field.column.name != 'id':
                args[field.column.name] = field.value

        for field in self.scheme.references.values():
            if field.id is not None:
                args[field.column.name] = field.id
                if isinstance(field.value, Model):
                    field.value.save()

        obj = self.selector.create(**args)
        if obj:
            self.id = obj.id
            self.exist_in_database = True
            self.updated = False
            return self
        else:
            raise Exception('Ошибка при получении идентификатора новой строки таблицы')

    def update(self):
        args = {}
        for field in self.scheme.simpleFields.values():
            if isinstance(field, ObjectField) and field.value is not None and field.column.name != 'id':
                args[field.column.name] = field.value

        for field in self.scheme.references.values():
            if field.id is not None:
                args[field.column.name] = field.id
                if issubclass(type(field.value), Model):
                    field.value.save()

        self.selector.filter(id=self.id).set(**args)
        self.exist_in_database = True
        self.updated = False
        return self

    def exists(self):
        if not self.exist_in_database:
            self.exist_in_database = self.selector.filter(id=self.id).exists()
        return self.exist_in_database

    def save(self):
        if self.updated:
            if self.id is not None and self.exists():
                self.update()
            else:
                self.insert()
        return self

    def load(self):
        data = self.selector.filter(id=self.id).getDict()
        if data:
            data = data[0]
            for key, value in data.items():
                if key in self.scheme.fields.keys():
                    field = self.scheme.fields[key]
                    if field is not None:
                        field.decode(value)
        return self

    def loadFromDBDict(self, row: dict):
        for key in row.keys():
            if key in self.scheme.simpleFields.keys():
                field = self.scheme.simpleFields[key]
            elif key[-2:] == 'Id' and key[:-2] in self.scheme.references.keys():
                field = self.scheme.references[key[:-2]]
            else:
                continue

            field.decode(row[key])
        self.updated = False

    def delete(self):
        self.selector.filter(id=self.id).delete()
        return self
