from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.src.Debug.Tester import UnitTester
from PyAsoka.MVC import model
from PyAsoka.Asoka import Asoka


class ModelTester(UnitTester):

    def test1(self):
        Logs.message('Models simple test', True)
        Asoka.databases.add(Asoka.DatabaseType.SQLITE, 'tests.db')

        class Person(model.Model, profile=Asoka.databases.tests):
            name = model.StrField().NOT_NULL()
            age = model.IntField().NOT_NULL()
            sex = model.BoolField().NOT_NULL()

        person = Person(name='Денчик', age=23, sex=True)
        person.save()
        pid = person.id
        # print(person)

        person = Person()
        person = Person(id=pid).load()
        self.breakPoint(person.name == 'Денчик' and person.age == 23 and person.sex is True)
        # print(person)

        person.name = 'Василиса'
        person.sex = False
        person.save()

        person = Person(id=pid).load()
        self.breakPoint(person.name == 'Василиса' and person.age == 23 and person.sex is False)
        # print(person)
        person.delete()

    def test2(self):
        Logs.message('Models references test', True)

        class Chat(model.Model, profile=Asoka.databases.tests):
            name = model.StrField()
            info = model.StrField()

        class Talker(model.Model, profile=Asoka.databases.tests):
            name = model.StrField()
            priority = model.IntField()
            chat = model.ManyToOne(Chat)

        chat = Chat(name='Петушарня', info='Чат для топовых петухов').save()

        Talker(name='Демьян', priority=3, chat=chat).save(),
        Talker(name='Андрей', priority=2, chat=chat).save(),
        Talker(name='Александр', priority=1, chat=chat).save(),
        Talker(name='Ден', priority=1, chat=chat).save()

        chat = Chat(id=chat.id)
        talkers = chat.talkerList()
        cond = True
        names = ['Демьян', 'Андрей', 'Александр', 'Ден']
        for i in range(len(talkers)):
            if talkers[i].name != names[i]:
                cond = False
            talkers[i].delete()
        self.breakPoint(cond)
        chat.delete()

    def test3(self):
        Logs.message('Models ManyToMany test', True)

        class Shop(model.Model, profile=Asoka.databases.tests):
            name = model.StrField()
            rating = model.FloatField()

        class People(model.Model, profile=Asoka.databases.tests):
            name = model.StrField()
            frequency = model.IntField()
            shop = model.ManyToMany(Shop)

        shop1 = Shop(name='Вкусвилл', rating=4.7).save()
        shop3 = Shop(name='Лента', rating=4.1).save()

        person1 = People(name='Борис', frequency=6).save()
        person2 = People(name='Евгений', frequency=11).save()
        person3 = People(name='Андрей', frequency=3).save()
        person4 = People(name='Владимир', frequency=5).save()

        shop1.addPeople(person1)
        shop1.addPeople(person3)
        shop1.addPeople(person4)

        person2.addShop(shop3)
        person4.addShop(shop3)

        cond1 = True
        cond2 = True
        personNames = ['Борис', 'Андрей', 'Владимир']
        shopNames = ['Вкусвилл', 'Лента']

        shop = Shop.objects.filter(name='Вкусвилл').first()
        persons = shop.peopleList()
        for i in range(len(persons)):
            if persons[i].name != personNames[i]:
                cond1 = False
        self.breakPoint(cond1)

        talker = People.objects.filter(name='Владимир').first()
        shops = talker.shopList()
        for i in range(len(shops)):
            if shops[i].name != shopNames[i]:
                cond2 = False
        self.breakPoint(cond2)

        People.objects.delete()
        Shop.objects.delete()


Asoka.databases.add(Asoka.DatabaseType.SQLITE, 'tests.db')
