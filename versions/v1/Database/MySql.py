import pymysql as sql
from PyAsoka.Instruments import Log


class MySql:
    class Constraints:
        PRIMARY_KEY = 1
        FOREIGN_KEY = 2
        AUTOINCREMENT = 3
        UNIQUE = 4
        NOT_NULL = 5
        DEFAULT = 6
        CHECK = 7

    connection = None
    host = ''
    user = ''
    password = ''
    database = ''

    @staticmethod
    def init(host, user, password, database):
        MySql.host = host
        MySql.user = user
        MySql.password = password
        MySql.database = database

    @staticmethod
    def connect():
        if MySql.connection is None or not MySql.connection.open:
            MySql.connection = sql.connect(
                host=MySql.host,
                user=MySql.user,
                password=MySql.password,
                database=MySql.database)
            cursor = MySql.connection.cursor()
            cursor.execute("SELECT VERSION()")
        else:
            cursor = MySql.connection.cursor()
        return cursor

    @staticmethod
    def getTables():
        cursor = MySql.connect()
        with MySql.connection:
            cursor.execute("SELECT `TABLE_NAME` FROM `information_schema`.`TABLES` "
                           "WHERE `TABLES`.`TABLE_SCHEMA` = 'mrKaribin$hotel_server';")
            MySql.connection.commit()
            return cursor.fetchall()

    @staticmethod
    def execute(query: str, params=None):
        if params is None:
            params = []
        cursor = MySql.connect()
        try:
            with MySql.connection:
                cursor.execute(query, params)
                MySql.connection.commit()
        except Exception:
            Log.warning(f"SQL execute exception: {query}")

    @staticmethod
    def query(query: str, params=[]):
        cursor = MySql.connect()
        try:
            with MySql.connection:
                cursor.execute(query, params)
                MySql.connection.commit()
                return cursor.fetchall()
        except Exception:
            Log.warning(f"SQL query exception: {query}")
            return {}
