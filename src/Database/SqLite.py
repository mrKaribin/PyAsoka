import sqlite3
import sqlite3 as sql
import threading
from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.src.Debug.Exceptions import Exceptions
from PyAsoka.src.Instruments.Timepoint import Timepoint
from PyAsoka.src.Database.DatabaseProfile import DatabaseProfile


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
    def connect(profile: DatabaseProfile):
        if SqLite.profile is None or SqLite.profile != profile or threading.current_thread().native_id != SqLite.thread_id:
            SqLite.profile = profile
            SqLite.connection = None
            SqLite.thread_id = threading.current_thread().native_id
            try:
                SqLite.connection = sql.connect(SqLite.profile.name)
                SqLite.connection.row_factory = dict_factory
                # Logs.message(f'Database connected from "{SqLite.profile.name}"')
                SqLite.cursor = SqLite.connection.cursor()
                SqLite.cursor.execute("PRAGMA foreign_keys = ON")
                return SqLite.cursor
            except sql.Error as error:
                Logs.error(f"SQL connect exception ({error})")
                return None

    @staticmethod
    def execute(query, params=None):
        try:
            if isinstance(SqLite.cursor, sqlite3.Cursor):
                Logs.message(f'{query} {params}')
                if params is None:
                    SqLite.cursor.execute(query)
                else:
                    SqLite.cursor.execute(query, params)
                SqLite.connection.commit()
        except sql.ProgrammingError as err:
            Logs.error(f'Программная ошибка в SQL запросе: {err}: {query}')
            return False
        except sql.DatabaseError as err:
            Logs.error(f'Ошибка работы БД: {err}: {query}')
            return False
        except Exception as e:
            Logs.error(f'Неизвестная ошибка при обращении к БД: {e}:{query}')
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
        SqLite.execute(f'SELECT MAX(id) FROM {table_name}')
        result = SqLite.cursor.fetchone()
        return result['MAX(id)'] if result is not None else None

    @staticmethod
    def getTableNames():
        SqLite.execute('SELECT name from sqlite_master where type = "table"')
        data = SqLite.cursor.fetchall()
        return [row['name'] for row in data]

    class Column:
        def __init__(self, name, datatype, primary_key=False, autoincrement=False, default=None, unique=False, check=None, not_null=True):
            self.name = name
            self.type = datatype
            self.primary_key = primary_key
            self.autoincrement = autoincrement
            self.default = default
            self.unique = unique
            self.check = check
            self.not_null = not_null

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
            from PyAsoka.src.MVC.ModelOld.Model import ModelContainer
            if datatype == int or issubclass(datatype, ModelContainer):
                return 'INTEGER'
            elif datatype == bool:
                return 'BOOLEAN'
            elif datatype == float:
                return 'FLOAT'
            elif datatype == bytes:
                return 'BLOB'
            elif datatype in (str, Timepoint):
                return 'TEXT'
            else:
                Exceptions.UnsupportableType(datatype)

    class Reference:
        def __init__(self, column, ref_table, ref_column, on_update=None, on_delete=None):
            self.column = column
            self.ref_table = ref_table
            self.ref_column = ref_column
            self.on_update = on_update
            self.on_delete = on_delete

    class Table:
        def __init__(self, profile: DatabaseProfile, name, columns=None, references=None):
            if references is None:
                references = []
            if columns is None:
                columns = []

            self.name = name
            self.profile = profile
            self.columns = columns
            self.references = references

        def add(self, value):
            if isinstance(value, SqLite.Column):
                self.columns.append(value)
            elif isinstance(value, SqLite.Reference):
                self.references.append(value)
            else:
                Exceptions.UnsupportableType(value)

        def isExist(self):
            SqLite.connect(self.profile)
            tables = SqLite.getTableNames()
            return self.name in tables

        def create(self):
            query = f'CREATE TABLE IF NOT EXISTS {self.name} ( '
            for column in self.columns:
                query += column.column_declaration() + ', '
            for reference in self.references:
                query += f'FOREIGN KEY ({reference.column.name}) REFERENCES {reference.ref_table.name} ({reference.ref_column.name})'
                if reference.on_update is not None:
                    query += f' ON UPDATE {reference.on_update}'
                if reference.on_delete is not None:
                    query += f' ON DELETE {reference.on_delete}'
                query += ', '
            query = query[:len(query) - 2] + ' );'
            # print(query)
            SqLite.execute(query)
