from PyAsoka.src.Database.DatabaseProfile import DatabaseProfile, DatabaseType
from PyAsoka.src.MVC.Model.ModelContainer import ModelContainer
from PyAsoka.src.MVC.Model.Selector import Selector
from PyAsoka.src.MVC.Model.Field import Field, ReferenceField
from PyAsoka.src.MVC.Model.ModelConfiguration import ModelConfiguration

import inspect


class Model:
    DatabaseType = DatabaseType
    DatabaseProfile = DatabaseProfile
    conf = ModelConfiguration(DatabaseProfile(DatabaseType.SQLITE), '')
    fields = {}
    references = {}
    containerType = None

    @classmethod
    def create_type(cls):
        fields = {
            'model': cls,
            '_fields_': cls.fields,
            '_references_': cls.references,
            'database': cls.conf.database,
            'table': cls.conf.table
        }

        name = cls.conf.table.name
        name = name[0].upper() + name[1:].lower()
        _type = type(f'{name}Object', (ModelContainer,), fields)
        return _type

    @classmethod
    def objects(cls):
        return Selector(cls)

    @classmethod
    def instance(cls, **kwargs) -> ModelContainer:
        return cls.containerType(**kwargs)

    @staticmethod
    def isContainerType(obj):
        return issubclass(type(obj), ModelContainer)

    @staticmethod
    def isModelType(obj):
        return issubclass(type(obj), Model)


def model(cls) -> Model:
    # print('\n', cls.__name__)
    cls = type(cls.__name__, (Model,), dict(cls.__dict__))
    cls.fields = {}
    cls.references = {}

    # Поиск пользовательского поля конфигурации модели
    for field in inspect.getmembers(cls, lambda value: isinstance(value, ModelConfiguration)):
        name, field = field
        if name != 'conf':
            cls.conf = field
            break

    # Поиск пользовательских полей модели
    cls.id = cls.conf.IntField().PRIMARY_KEY().AUTOINCREMENT().NOT_NULL()
    for field in inspect.getmembers(cls, lambda value: isinstance(value, Field) and not isinstance(value, ReferenceField)):
        # print(field)
        name, field = field
        field.setName(name)
        cls.fields[field.name] = field

    # Поиск пользовательских зависимостей
    for field in inspect.getmembers(cls, lambda value: isinstance(value, ReferenceField)):
        name, field = field
        field.setName(name)
        cls.references[field.column.name] = field
        cls.conf.table.references.append(cls.conf.database.Reference(
            field.column.name,
            field.ref_class.conf.table.name,
            field.ref_field.column.name,
            field._on_update_,
            field._on_delete_
        ))

    # Если существуют поля кроме id, проверяем существование таблицы в БД
    if len(cls.fields) > 1:
        if not cls.conf.table.isExist():
            cls.conf.table.create()
        cls.containerType = cls.create_type()
    return cls
