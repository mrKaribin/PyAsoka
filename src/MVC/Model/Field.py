from PyAsoka.Asoka import Asoka


class Field:
    def toColumn(self, _type: Asoka.DatabaseType):
        pass


class SimpleField(Field):
    def __init__(self, name, datatype, value=None):
        self.autoload = False
        self.autosave = False
        self.loadOnRequest = False
        self.name = name
        self.type = datatype
        self.defaultValue = value
        self.primary_key = False
        self.autoincrement = False
        self.default = None
        self.unique = False
        self.check = None
        self.not_null = False
        self.column = None

    def toColumn(self, _type: Asoka.DatabaseType):
        if _type == Asoka.DatabaseType.SQLITE:
            from PyAsoka.src.Database.SqLite import SqLite
            return SqLite.Column(
                self.name,
                SqLite.Column.toSqlType(self.type),
                self.primary_key,
                self.autoincrement,
                self.default,
                self.unique,
                self.check,
                self.not_null
            )

    def PRIMARY_KEY(self):
        self.primary_key = True
        return self

    def AUTOINCREMENT(self):
        self.autoincrement = True
        return self

    def UNIQUE(self):
        self.unique = True
        return self

    def NOT_NULL(self):
        self.not_null = True
        return self

    def DEFAULT(self, value):
        self.default = value
        return self

    def CHECK(self, condition):
        self.check = condition
        return self

    def LOAD_ON_REQUEST(self, value=True):
        self.loadOnRequest = value

    def UPDATEABILITY(self, load, save):
        self.autoload = load
        self.autosave = save


class IntField(SimpleField):
    def __init__(self, value=None):
        super(IntField, self).__init__('', int, value)


class FloatField(SimpleField):
    def __init__(self, value=None):
        super(FloatField, self).__init__('', float, value)


class BoolField(SimpleField):
    def __init__(self, value=None):
        super(BoolField, self).__init__('', bool, value)


class StrField(SimpleField):
    def __init__(self, value=None):
        super(StrField, self).__init__('', str, value)


class BinaryField(SimpleField):
    def __init__(self, value=None):
        super(BinaryField, self).__init__('', bytes, value)


class Reference(Field):
    pass


class OneToOne(Reference):
    def __init__(self, model, value=None):
        self.autoload = False
        self.autosave = False
        self.name = ''
        self.defaultValue = value
        self.model = model
        self.column = None
        self.default = None
        self.unique = False
        self.not_null = False

    def toColumn(self, _type: Asoka.DatabaseType):
        if _type == Asoka.DatabaseType.SQLITE:
            from PyAsoka.src.Database.SqLite import SqLite
            return SqLite.Column(
                self.name + 'Id',
                'INTEGER',
                default=self.default,
                unique=self.unique,
                not_null=self.not_null
            )

    def toReference(self, _type: Asoka.DatabaseType):
        if _type == Asoka.DatabaseType.SQLITE:
            column = self.toColumn(_type)
            from PyAsoka.src.Database.SqLite import SqLite
            return SqLite.Reference(
                column,
                self.model.scheme.table,
                self.model.scheme.fields['id'].column
            )

    def UNIQUE(self):
        self.unique = True
        return self

    def NOT_NULL(self):
        self.not_null = True
        return self

    def DEFAULT(self, value):
        self.default = value
        return self

    def UPDATEABILITY(self, load, save):
        self.autoload = load
        self.autosave = save


class OneToMany(Reference):
    def __init__(self, model, column):
        self.model = model
        self.column = column


class ManyToOne(OneToOne):
    def __init__(self, model, value=None, listname=None):
        super().__init__(model, value)
        self.listname = listname


class ManyToMany:
    def __init__(self, model, listname=None):
        self.scheme = None
        self.model1 = None
        self.model2 = model
        self.listname = listname

    def create(self, model):
        from PyAsoka.src.MVC.Model.Model import Model, ModelMeta, ModelScheme
        self.model1 = model

        name = self.model1().__class__.__name__
        name1 = name[0].upper() + name[1:]
        fieldName1 = name[0].lower() + name[1:]
        name = self.model2().__class__.__name__
        name2 = name[0].upper() + name[1:]
        fieldName2 = name[0].lower() + name[1:]
        tableName = f'{name1}And{name2}Link'

        scheme = ModelScheme(self.model1.scheme.profile, tableName)
        col1 = scheme.database.Column(fieldName1 + 'Id', 'INTEGER')
        scheme.table.add(col1)
        scheme.table.add(scheme.database.Reference(col1,
                                                   self.model1.scheme.table,
                                                   self.model1.scheme.fields['id'].column,
                                                   on_delete='CASCADE',
                                                   on_update='CASCADE'))
        col2 = scheme.database.Column(fieldName2 + 'Id', 'INTEGER')
        scheme.table.add(col2)
        scheme.table.add(scheme.database.Reference(col2,
                                                   self.model2.scheme.table,
                                                   self.model2.scheme.fields['id'].column,
                                                   on_delete='CASCADE',
                                                   on_update='CASCADE'))

        scheme.database.connect(scheme.profile)
        if not scheme.table.isExist():
            scheme.table.create()
        self.scheme = scheme

        return ManyToManyField(self.model2, scheme, col1, col2), ManyToManyField(self.model1, scheme, col2, col1)


class ManyToManyField(Reference):
    def __init__(self, model, scheme, column, ref_column):
        self.model = model
        self.scheme = scheme
        self.column = column
        self.refColumn = ref_column
