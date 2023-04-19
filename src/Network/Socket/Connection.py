from PyAsoka.src.Network.Socket.Socket import Socket
from PyAsoka.src.Network.Socket.Message import SocketMessage

from enum import IntEnum


class Connection(Socket):
    class State(IntEnum):
        CONNECTED = 1
        DISCONNECTED = 2
        SENDING = 3
        READING = 4

    def __init__(self, connection, address, card):
        super().__init__()
        self._socket_ = connection
        self._ip_ = address[0]
        self._port_ = address[1]
        self._state_ = Connection.State.CONNECTED
        self._card_ = card

    @property
    def connection(self):
        return self._socket_

    @property
    def address(self):
        return self._ip_, self._port_

    @property
    def card(self):
        return self._card_

    def reply(self, message: SocketMessage, data: dict = None):
        if data is None:
            data = {}

        if message.isRequest():
            data['request'] = message.json['request']
            header = message.json['request']['header']
            self.send(header, data)

    def close(self):
        self.connection.close()

