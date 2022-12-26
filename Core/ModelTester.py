from PyAsoka.Debug.Logs import Logs
from PyAsoka.Debug.Tester import UnitTester
from PyAsoka.Core.Model import model, ModelConfiguration, ADatabaseProfile, DatabaseType


class ModelTester(UnitTester):
    database = ADatabaseProfile(DatabaseType.SQLITE, 'tests.db')

    def modelsSimpleTest(self):
        Logs.message('Models simple test')

        @model
        class Person:
            conf = ModelConfiguration(self.database, 'Person')
            name = conf.StrField().NOT_NULL()
            age = conf.IntField().NOT_NULL()
            sex = conf.BoolField().NOT_NULL()

        person = Person.instance(name='Денчик', age=23, sex=True)
        person.save()
        pid = person.id
        # print(person)

        person = Person.instance(id=pid).load()
        self.breakPoint(person.name == 'Денчик' and person.age == 23 and person.sex is True)
        # print(person)

        person.name = 'Василиса'
        person.sex = False
        person.save()

        person = Person.instance(id=pid).load()
        self.breakPoint(person.name == 'Василиса' and person.age == 23 and person.sex is False)
        # print(person)
        person.delete()

    def modelsForeignKeyTest(self):

        @model
        class Chat:
            conf = ModelConfiguration(self.database, 'Chat')
            name = conf.StrField()
            info = conf.StrField()

        @model
        class Talker:
            settings = ModelConfiguration(self.database, 'Talker')
            name = settings.StrField()
            priority = settings.IntField()

        chat = Chat.objects().create(name='Гипермаркеты', info='Продаем если купите')

        market1 = Talker.objects().create(name='Пятерочка', priority=2)
        market2 = Talker.objects().create(name='Перекрёсток', priority=3)

        print(chat)
        print(market1)
        print(market2)
