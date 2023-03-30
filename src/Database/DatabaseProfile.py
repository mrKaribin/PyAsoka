from enum import Enum, auto
from PyAsoka.src.Debug.Exceptions import Exceptions


class DatabaseType(Enum):
    SQLITE = 'SQLITE'
    MYSQL = 'MYSQL'


class DatabaseProfile:
    def __init__(self, lang=DatabaseType.SQLITE, name=None, user=None, password=None):
        self.type = lang
        self.name = name
        self.user = user
        self.password = password
        self.driver = None

    def getDriver(self):
        if self.driver is None:
            if self.type == DatabaseType.SQLITE:
                from PyAsoka.src.Database.SqLite import SqLite as database
            elif self.type == DatabaseType.MYSQL:
                from PyAsoka.src.Database.MySql import MySql as database
            else:
                Exceptions.UnsupportableType(self.type)

            self.driver = database
        return self.driver

    def connect(self):
        database = self.getDriver()
        database.connect(self)
