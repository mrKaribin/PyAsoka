import json as JSON
import jwt


class SocketMessage:
    def __init__(self, header, json=None):
        self._header_ = header
        self._json_ = json
        # self._data_ = data

    @property
    def header(self):
        return self._header_

    @property
    def json(self):
        return self._json_

    def encode(self, key):
        header_data = self._header_.encode('utf-8')
        header_size = len(header_data)
        json_data = self.encrypt(self._json_, key).encode('utf-8')
        json_size = len(json_data)

        data = b''
        data += header_size.to_bytes(4, 'big')
        data += json_size.to_bytes(4, 'big')
        data += header_data
        data += json_data
        return data

    @staticmethod
    def decode(data, key):
        header_size = int.from_bytes(data[:4], 'big')
        json_size = int.from_bytes(data[4:8], 'big')

        header_end = 8 + header_size
        header = data[8:header_end].decode('utf-8')
        json_end = header_end + json_size
        json = SocketMessage.decrypt(data[header_end:json_end].decode('utf-8'), key)
        return SocketMessage(header, json)

    @staticmethod
    def encrypt(data, key):
        return jwt.encode(data, key, algorithm="HS256")

    @staticmethod
    def decrypt(data, key):
        return jwt.decode(data, key, algorithms=["HS256"])

