import sqlite3
import sqlite3 as sql
import threading
from enum import Enum
from PyAsoka.Debug.Logs import Logs
from PyAsoka.Instruments.ATimepoint import ATimepoint
from PyAsoka.Database.ADatabaseTable import ADatabaseProfile


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SqLite:
    connection = None
    thread_id = None
    lastRowId = None
    profile = None
    cursor = None

    @staticmethod
    def connect(profile: ADatabaseProfile):
        if SqLite.profile is None or SqLite.profile != profile or threading.current_thread().native_id != SqLite.thread_id:
            SqLite.profile = profile
            SqLite.connection = None
            SqLite.thread_id = threading.current_thread().native_id
            try:
                SqLite.connection = sql.connect(SqLite.profile.name)
                SqLite.connection.row_factory = dict_factory
                # Logs.message(f'Database connected from "{SqLite.profile.name}"')
                SqLite.cursor = SqLite.connection.cursor()
                return SqLite.cursor
            except sql.Error as error:
                Logs.error(f"SQL connect exception ({error})")
                return None

    @staticmethod
    def execute(query, params=None):
        try:
            if isinstance(SqLite.cursor, sqlite3.Cursor):
                # Logs.message(query)
                if params is None:
                    SqLite.cursor.execute(query)
                else:
                    SqLite.cursor.execute(query, params)
                SqLite.connection.commit()
        except sql.ProgrammingError as err:
            Logs.error(f'Программная ошибка в SQL запросе: {query}')
            return False
        except sql.DatabaseError as err:
            Logs.error(f'Ошибка работы БД: {query}')
            return False
        except Exception as e:
            Logs.error(f'Неизвестная ошибка при обращении к БД: {e}: {query}')
            return False
        return True

    @staticmethod
    def query(query, params=None):
        if SqLite.execute(query, params):
            return SqLite.cursor.fetchall()
        else:
            return False

    @staticmethod
    def getLastAutoincrement(table_name):
        SqLite.execute(f'SELECT seq FROM sqlite_sequence where name="{table_name}"')
        result = SqLite.cursor.fetchone()
        return result['seq'] if result is not None else None

    @staticmethod
    def getTableNames():
        SqLite.execute('SELECT name from sqlite_master where type = "table"')
        data = SqLite.cursor.fetchall()
        return [row['name'] for row in data]

    class Column:
        def __init__(self, name, datatype):
            self.name = name
            self.type = datatype
            self.primary_key = False
            self.autoincrement = False
            self.default = None
            self.unique = False
            self.check = None
            self.not_null = False

        def PRIMARY_KEY(self):
            self.primary_key = True
            return self

        def AUTOINCREMENT(self):
            self.autoincrement = True
            return self

        def UNIQUE(self):
            self.unique = True
            return self

        def NOT_NULL(self):
            self.not_null = True
            return self

        def DEFAULT(self, value):
            self.default = value
            return self

        def CHECK(self, condition):
            self.check = condition
            return self

        def column_declaration(self):
            decl = f'{self.name} {self.type}'
            if self.primary_key:
                decl += ' PRIMARY KEY'
            if self.autoincrement:
                decl += ' AUTOINCREMENT'
            if self.unique:
                decl += ' UNIQUE'
            if self.not_null:
                decl += ' NOT NULL'
            if self.default is not None:
                decl += ' DEFAULT '
                if isinstance(self.default, str) or isinstance(self.default, bytes):
                    decl += f'"{self.default}"'
                else:
                    decl += str(self.default)
            if self.check is not None:
                decl += f' CHECK ({self.check})'
            return decl

        @staticmethod
        def toSqlType(datatype):
            from PyAsoka.Core.Model import ModelContainer
            if datatype == int or issubclass(datatype, ModelContainer):
                return 'INTEGER'
            elif datatype == bool:
                return 'BOOLEAN'
            elif datatype == float:
                return 'FLOAT'
            elif datatype == bytes:
                return 'BLOB'
            elif datatype in (str, ATimepoint):
                return 'TEXT'
            else:
                Logs.exception_unsupportable_type(datatype)

    class Reference:
        class Mode(Enum):
            CASCADE = 'CASCADE'
            SET_NULL = 'SET NULL'
            RESTRICT = 'RESTRICT'
            NO_ACTION = 'NO ACTION'
            SET_DEFAULT = 'SET DEFAULT'

        def __init__(self, key, table, column):
            self.key = key
            self.table = table
            self.column = column
            self._on_update_ = None
            self._on_delete_ = None

        def ON_UPDATE_CASCADE(self):
            self._on_update_ = 'CASCADE'

        def ON_UPDATE_RESTRICT(self):
            self._on_update_ = 'CASCADE'

        def ON_UPDATE_SET_NULL(self):
            self._on_update_ = 'SET NULL'

        def ON_UPDATE_SET_DEFAULT(self):
            self._on_update_ = 'SET DEFAULT'

        def ON_DELETE_CASCADE(self):
            self._on_delete_ = 'CASCADE'

        def ON_DELETE_RESTRICT(self):
            self._on_delete_ = 'CASCADE'

        def ON_DELETE_SET_NULL(self):
            self._on_delete_ = 'SET NULL'

        def ON_DELETE_SET_DEFAULT(self):
            self._on_delete_ = 'SET DEFAULT'

    class Table:
        def __init__(self, profile: ADatabaseProfile, name, columns=None, references=None):
            if references is None:
                references = []
            if columns is None:
                columns = []

            self.name = name
            self.profile = profile
            self.columns = columns
            self.references = references

        def isExist(self):
            SqLite.connect(self.profile)
            tables = SqLite.getTableNames()
            return self.name in tables

        def create(self):
            query = f'CREATE TABLE IF NOT EXISTS {self.name} ( '
            for column in self.columns:
                query += column.column_declaration() + ', '
            for reference in self.references:
                query += f'FOREIGN KEY ({reference.key}) REFERENCES {reference.table} ({reference.column})'
                if reference._on_update_ is not None:
                    query += f' ON UPDATE {reference._on_update_}'
                if reference._on_delete_ is not None:
                    query += f' ON DELETE {reference._on_delete_}'
                query += ', '
            query = query[:len(query) - 2] + ' );'
            # print(query)
            SqLite.execute(query)
