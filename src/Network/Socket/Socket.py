from PyAsoka.src.Network.Socket.Message import SocketMessage

import socket


class Socket:
    def __init__(self):
        self._socket_ = socket.socket()
        self._server_ = None
        self._secret_ = None

    @property
    def socket(self):
        return self._socket_

    @property
    def server(self):
        return self._server_

    @property
    def bound(self):
        return self._server_ is not None

    @property
    def secret(self):
        return self._secret_

    def setSecret(self, secret):
        self._secret_ = secret

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
        self.socket.sendall(SocketMessage(header, json).encode(self.getSecret()))

    def getSecret(self):
        from PyAsoka.Asoka import Asoka
        return Asoka.Project.secret if self.secret is None else self.secret

    def createKey(self):
        from random import randint
        key = ''
        for i in range(16):
            key += '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'[randint(0, 35)]
        return key

    def close(self):
        self.socket.close()
        self._socket_ = socket.socket()

    @staticmethod
    def readFromConnection(connection, key=None):
        from PyAsoka.Asoka import Asoka
        if isinstance(connection, Socket):
            if key is None:
                key = connection.getSecret()
            connection = connection.socket
        else:
            if key is None:
                key = Asoka.Project.secret

        try:
            data = connection.recv(4)
            if data:
                if len(data) > 0:
                    if len(data) < 4:
                        print('PIZDEC SLUCHILSYA')
                    total = int.from_bytes(data[:2], 'big') + int.from_bytes(data[2:], 'big')
                    while len(data) < total + 4:
                        data += connection.recv(1024)
                    return SocketMessage.decode(data, key)
                else:
                    return None
            else:
                return False
        except Exception as e:
            # print(e)
            return False
