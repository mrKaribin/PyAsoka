from PyAsoka.src.MVC.Model.Model import Model, DatabaseProfile, DatabaseType

import random


class Params(Model):
    def __init__(self):
        super(Params, self).__init__(DatabaseProfile(DatabaseType.SQLITE, 'tests.db', 'admin', 'password'), 'Parameters')

        self.id = self.IntField('id').PRIMARY_KEY().AUTOINCREMENT().UNIQUE().NOT_NULL()
        self.growth = self.IntField('growth').NOT_NULL()
        self.weight = self.IntField('weight').NOT_NULL()
        self.coef = self.FloatField('coef').NOT_NULL()

        self.initialization()


class People(Model):
    def __init__(self):
        super(People, self).__init__(DatabaseProfile(DatabaseType.SQLITE, 'tests.db', 'admin', 'password'), 'People')

        self.id = self.IntField('id').PRIMARY_KEY().AUTOINCREMENT().UNIQUE().NOT_NULL()
        self.name = self.StrField('name').NOT_NULL()
        self.age = self.IntField('age').NOT_NULL()
        self.params = self.AField('params_id', 'Params', 'id', Params).NOT_NULL()

        self.initialization()

    @staticmethod
    def fromId(_id: int):
        people = People()
        people.id.set(_id)
        people.load()
        return people


def generate_dataset():
    names = ['Вадим', 'Андрей', 'Виктор', 'Антон', 'Сергей', 'Владимир', 'Евгений', 'Денис']

    for i in range(20):
        obj = People()
        obj.name.set(names[random.randint(0, 7)])
        obj.age.set(random.randint(16, 55))
        params = Params()
        params.growth.set(random.randint(150, 190))
        params.weight.set(random.randint(40, 100))
        params.coef.set(params.growth() / params.weight())
        obj.params.set(params)
        obj.save()


# generate_dataset()

person = People()
print(person.name.distinct())
