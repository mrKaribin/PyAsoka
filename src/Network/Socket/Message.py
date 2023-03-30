import json as JSON


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

    def encode(self):
        header_data = self._header_.encode('utf-8')
        header_size = len(header_data)
        json_data = JSON.dumps(self._json_).encode('utf-8')
        json_size = len(json_data)
        # data_size = len(self._data_)

        data = b''
        data += header_size.to_bytes(4, 'big')
        data += json_size.to_bytes(4, 'big')
        # data += data_size.to_bytes(4, 'big')
        data += header_data
        data += json_data
        # data += self._data_
        return data

    @staticmethod
    def decode(data):
        header_size = int.from_bytes(data[:4], 'big')
        json_size = int.from_bytes(data[4:8], 'big')
        # data_size = int.from_bytes(data[4:8], 'big')

        header_end = 8 + header_size
        header = data[8:header_end].decode('utf-8')
        json_end = header_end + json_size
        json = JSON.loads(data[header_end:json_end].decode('utf-8'))
        return SocketMessage(header, json)

