from PyAsoka.src.Network.Socket.Message import SocketMessage

import socket


class Socket:
    def __init__(self):
        self._socket_ = socket.socket()
        self._server_ = None

    @property
    def socket(self):
        return self._socket_

    @property
    def server(self):
        return self._server_

    @property
    def bound(self):
        return self._server_ is not None

    def bind(self, host='', port='12550'):
        self._server_ = (host, port)
        self.socket.bind((host, port))

    def connect(self, host, port):
        self.socket.connect((host, port))

    def listen(self, num):
        self.socket.listen(num)

    def accept(self):
        return self._socket_.accept()

    def send(self, header: str, json: dict):
        self.socket.sendall(SocketMessage(header, json).encode())

    @staticmethod
    def readFromConnection(connection):
        from PyAsoka.src.Network.Socket.Connection import Connection
        if isinstance(connection, Connection):
            connection = connection.connection

        try:
            data = connection.recv(4)
            if data:
                if len(data) > 0:
                    if len(data) < 4:
                        print('PIZDEC SLUCHILSYA')
                    total = int.from_bytes(data[:2], 'big') + int.from_bytes(data[2:], 'big')
                    while len(data) < total + 4:
                        data += connection.recv(1024)
                    return SocketMessage.decode(data)
                else:
                    return None
            else:
                return False
        except Exception as e:
            return False
