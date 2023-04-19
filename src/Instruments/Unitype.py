from PyAsoka.src.Debug.Exceptions import Exceptions

import json as JSON


class Unitype:
    def __init__(self, data=None):
        self.type = ''
        self.data = None
        if data is not None:
            self.encode(data)

    def encode(self, data):
        from PyAsoka.src.Instruments.Timepoint import Timepoint

        if isinstance(data, int):
            datatype = 'int'
            data = str(data)
        elif isinstance(data, float):
            datatype = 'float'
            data = str(data)
        elif isinstance(data, bool):
            datatype = 'bool'
            data = str(data)
        elif isinstance(data, str):
            datatype = 'str'
            data = data
        elif isinstance(data, bytes):
            datatype = 'bytes'
            data = str(data)
        elif isinstance(data, dict):
            datatype = 'dict'
            data = JSON.dumps(data)
        elif isinstance(data, list):
            datatype = 'list'
            data = JSON.dumps(data)
        elif isinstance(data, tuple):
            datatype = 'tuple'
            data = JSON.dumps(data)
        elif isinstance(data, Timepoint):
            datatype = 'Timepoint'
            data = JSON.dumps(data.toDict())
        else:
            Exceptions.UnsupportableType(data)

        self.type = datatype
        self.data = data

    def decode(self):
        from PyAsoka.src.Instruments.Timepoint import Timepoint

        if self.type == 'int':
            return int(self.data)
        elif self.type == 'float':
            return float(self.data)
        elif self.type == 'bool':
            return bool(self.data)
        elif self.type == 'str':
            return str(self.data)
        elif self.type == 'bytes':
            return bytes(self.data)
        elif self.type == 'dict':
            return JSON.loads(self.data)
        elif self.type == 'list':
            return JSON.loads(self.data)
        elif self.type == 'tuple':
            return JSON.loads(self.data)
        elif self.type == 'Timepoint':
            return Timepoint.fromDict(JSON.loads(self.data))
        else:
            raise Exception(f'Неизвестный тип данных {self.type}')

    def toDict(self):
        return {
            'type': self.type,
            'data': self.data
        }

    @staticmethod
    def fromDict(data: dict):
        var = Unitype()
        var.type = data.get('type')
        var.data = data.get('data')
        return var

    def toBytes(self):
        return bytes(JSON.dumps(self.toDict(),), 'utf-8')

    @staticmethod
    def fromBytes(data):
        return Unitype.fromDict(JSON.loads(str(data, 'utf-8')))
