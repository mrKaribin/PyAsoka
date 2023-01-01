from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.src.Debug.Tester import UnitTester
from PyAsoka.src.MVC.Model.Model import model, ModelConfiguration, DatabaseProfile, DatabaseType


class ModelTester(UnitTester):
    database = DatabaseProfile(DatabaseType.SQLITE, 'tests.db')

    def test1(self):
        Logs.message('Models simple test', True)

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

    def test2(self):
        Logs.message('Models references test', True)

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
            chat = settings.Reference(Chat, Chat.id)

        chat = Chat.instance(name='Петушарня', info='Чат для топовых петухов').save()

        dema = Talker.instance(name='Демьян', priority=3, chat=chat).save()
        fill = Talker.instance(name='Андрей', priority=2, chat=chat).save()
        alex = Talker.instance(name='Александр', priority=1, chat=chat).save()
        den = Talker.instance(name='Ден', priority=1, chat=chat).save()

        print(dema.chat)
