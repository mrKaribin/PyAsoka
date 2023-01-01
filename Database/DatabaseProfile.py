from enum import Enum, auto


class DatabaseType(Enum):
    SQLITE = auto()
    MYSQL = auto()


class DatabaseProfile:
    def __init__(self, lang=DatabaseType.SQLITE, name=None, user=None, password=None):
        self.lang = lang
        self.name = name
        self.user = user
        self.password = password
        self.driver = None

    def getDriver(self):
        if self.driver is None:
            if self.lang == DatabaseType.SQLITE:
                from PyAsoka.Database.SqLite import SqLite as database
            elif self.lang == DatabaseType.MYSQL:
                from PyAsoka.Database.MySql import MySql as database

            self.driver = database
        return self.driver

    def connect(self):
        database = self.getDriver()
        database.connect(self)
