import os
import json
from pathlib import Path


class File:
    def __init__(self, path: str):
        self.path = ''          # Полный путь
        self.name = ''          # Имя + расширение
        self.stem = ''          # Имя
        self.suffix = ''        # Расширение
        self.change(path)

    def __str__(self):
        return f'<File: {self.path}>'

    def change(self, path):
        if os.path.isabs(path):
            self.path = path
        else:
            self.path = os.path.abspath(path)

        path = Path(self.path)
        self.name = path.name
        self.stem = path.stem
        self.suffix = path.suffix[1:]

    def exist(self):
        return os.path.exists(self.path)

    def check_exists(self):
        if not os.path.exists(self.path):
            raise Exception(f'Файл по адресу {self.path} не существует')

    def read(self):
        self.check_exists()
        file = open(self.path, 'r')
        result = file.read()
        file.close()
        return result

    def read_bytes(self):
        self.check_exists()
        file = open(self.path, 'rb')
        result = file.read()
        file.close()
        return result

    def read_json(self):
        self.check_exists()
        file = open(self.path, 'r')
        result = json.loads(file.read())
        file.close()
        return result

    def write(self, data):
        self.check_exists()
        file = open(self.path, 'r')
        file.write(data)
        file.close()

    def write_bytes(self, data):
        self.check_exists()
        file = open(self.path, 'wb')
        file.write(data)
        file.close()

    def write_json(self, _json):
        self.check_exists()
        file = open(self.path, 'r')
        file.write(json.dumps(json))
        file.close()
