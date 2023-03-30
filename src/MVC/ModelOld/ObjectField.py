from PyAsoka.Debug import Exceptions
from PyAsoka.src.MVC.ModelOld.Field import Field, ReferenceField


class ObjectField:
    def __init__(self, obj, field: Field, value):
        from PyAsoka.MVC import ModelContainer
        if not isinstance(obj, ModelContainer):
            raise Exceptions.UnsupportableType(obj)

        self.object = obj
        self.column = field.column
        self.database = self.object.database
        self.type = field.type
        self.value = value
        self.autoload = field.autoload
        self.autosave = field.autosave

        self.fromSql = field.fromSql
        # self.object.table.columns.append(self.column)

    def __call__(self):
        return self.get(self)

    def set(self, obj, value):
        if isinstance(value, self.type) or value is None:
            self.value = value
            if self.autosave and self.object.exist_in_database:
                self.save()
            else:
                self.object.updated = True
        else:
            Exceptions.UnsupportableType(value)

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
        obj_id = self.object.id
        if obj_id is not None:
            self.database.connect(self.database.profile)
            data = self.database.query(f'SELECT {self.column.name} FROM {self.object.table.name} WHERE id=?', [obj_id])
            self.value = self.fromSql(data[self.column.name])

    def save(self):
        obj_id = self.object.id
        if obj_id is not None:
            self.database.connect(self.database.profile)
            self.database.execute(f'UPDATE {self.object.table.name} SET {self.column.name}=? WHERE id=?;', [self.value, obj_id])


class ObjectReference(ObjectField):
    def __init__(self, obj, field: ReferenceField, value, value_id):
        super().__init__(obj, field, value)
        if value is not None and value_id is None:
            value_id = value.id
        self.id = value_id
        self.ref_class = field.ref_class
        self.ref_field = field.ref_field

    def set(self, obj, value):
        super().set(obj, value)

        if value is not None:
            self.id = value.id
        else:
            self.id = None

        if self.autosave and self.object.exist_in_database:
            self.saveId()
        else:
            self.object.updated = True

    def get(self, obj):
        if self.autoload and self.object.exist_in_database:
            self.load()
        if self.value is None and self.id is not None:
            self.value = self.ref_class.containerType(id=self.id)
            self.value.load()
        return self.value

    def setId(self, obj, value_id):
        self.id = value_id
        if self.autosave and self.object.exist_in_database:
            self.saveId()
        else:
            self.object.updated = True

    def getId(self, obj):
        if self.autoload and self.object.exist_in_database:
            self.loadId()
        return self.id

    def saveId(self):
        obj_id = self.object.id
        if obj_id is not None:
            self.database.connect(self.database.profile)
            self.database.query(f'UPDATE {self.object.table.name} SET {self.column.name}=? WHERE id=?;', [self.id, obj_id])

    def loadId(self):
        obj_id = self.object.id
        if obj_id is not None:
            self.database.connect(self.database.profile)
            data = self.database.query(f'SELECT {self.column.name} FROM {self.object.table.name} WHERE id=?', [obj_id])
            self.id = int(data[self.column.name])

    def save(self):
        self.saveId()
        if self.value is not None:
            self.value.save()

    def load(self):
        if self.id is not None:
            self.value = self.ref_class.containerType(id=self.id)
            self.value.load()