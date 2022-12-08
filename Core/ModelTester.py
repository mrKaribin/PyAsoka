from PyAsoka.Debug.Logs import Logs
from PyAsoka.Debug.Tester import UnitTester
from PyAsoka.Core.AModel import AModel, model


class ModelTester(UnitTester):
    database = AModel.DatabaseProfile(AModel.DatabaseType.SQLITE, 'tests.db')

    def modelsSimpleTest(self):
        Logs.message('Models simple test')

        @model
        class Person(AModel):
            settings = AModel.createSettings(self.database, 'Person')
            name = settings.StrField().NOT_NULL()
            age = settings.IntField().NOT_NULL()
            sex = settings.BoolField().NOT_NULL()

        person = Person.instance(name='Денчик', age=23, sex=True)
        person.save()
        pid = person.id
        print(person)

        person = Person.instance(id=pid).load()
        self.breakPoint(person.name == 'Денчик' and person.age == 23 and person.sex is True)
        print(person)

        person.name = 'Василиса'
        person.sex = False
        person.save()

        person = Person.instance(id=pid).load()
        self.breakPoint(person.name == 'Василиса' and person.age == 23 and person.sex is False)
        print(person)
        person.delete()

    def modelsForeignKeyTest(self):

        @model
        class Chat(AModel):
            settings = AModel.createSettings(self.database, 'Chat')
            name = settings.StrField()
            info = settings.StrField()

        @model
        class Talker(AModel):
            settings = AModel.createSettings(self.database, 'Talker')
            name = settings.StrField()
            priority = settings.IntField()

        chat = Chat.objects().create(name='Гипермаркеты', info='Продаем если купите')

        market1 = Talker.objects().create(name='Пятерочка', priority=2)
        market2 = Talker.objects().create(name='Перекрёсток', priority=3)

        print(chat)
        print(market1)
        print(market2)
