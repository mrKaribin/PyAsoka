from PyAsoka.src.Database.DatabaseProfile import DatabaseProfile, DatabaseType


class Databases:
    def __init__(self):
        self._databases_ = {}
        self.add(DatabaseType.SQLITE, 'asoka.db')

    def add(self, lang: DatabaseType, name: str, user: str = None, password: str = None):
        key = name[:name.find('.')]
        profile = DatabaseProfile(lang, name, user, password)
        self._databases_[key] = profile
        self.__dict__.update({key: profile})

    def get(self, name):
        if name in self._databases_.keys():
            return self._databases_[name]
