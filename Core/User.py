

class User:
    freeID = 1
    all = {}

    def __init__(self, name, surname=None, patronymic=None):
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.id = User.freeID
        User.freeID += 1
        User.all[self.id] = self

    @staticmethod
    def find(_id):
        return User.all[_id]


class UsersManager:
    def __init__(self):
        self._users_ = {}

    def create(self, name, surname=None, patronymic=None):
        user = User(name, surname, patronymic)
        self._users_[user.id] = user
        return user

    def find(self, _id):
        return self._users_[_id]
