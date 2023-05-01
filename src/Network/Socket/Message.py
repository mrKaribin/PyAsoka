import json as JSON
import jwt


class SocketMessage:
    def __init__(self, header, json=None):
        self._header_ = header
        self._json_ = json

    @property
    def header(self):
        return self._header_

    @property
    def json(self) -> dict:
        return self._json_

    def isRequest(self):
        return self.json.get('request') is not None

    def encode(self, key):
        from PyAsoka.Asoka import Asoka
        header_data = self._header_.encode('utf-8')
        header_size = len(header_data)
        json_data = Asoka.encrypt(JSON.dumps(self._json_).encode('utf-8'))
        json_size = len(json_data)

        data = b''
        data += header_size.to_bytes(4, 'big')
        data += json_size.to_bytes(4, 'big')
        data += header_data
        data += json_data
        return data

    @staticmethod
    def decode(data, key):
        from PyAsoka.Asoka import Asoka
        header_size = int.from_bytes(data[:4], 'big')
        json_size = int.from_bytes(data[4:8], 'big')

        header_end = 8 + header_size
        header = data[8:header_end].decode('utf-8')
        json_end = header_end + json_size
        json = JSON.loads(Asoka.decrypt(str(data[header_end:json_end], 'utf-8')))
        return SocketMessage(header, json)

    @staticmethod
    def encrypt(data, key):
        return jwt.encode(data, key, algorithm="HS256")

    @staticmethod
    def decrypt(data, key):
        return jwt.decode(data, key, algorithms=["HS256"])

