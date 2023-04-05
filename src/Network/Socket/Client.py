from PyAsoka.src.Network.Socket.Socket import Socket
from PyAsoka.src.Network.Socket.Connection import Connection
from PyAsoka.src.Network.Socket.Message import SocketMessage
from PyAsoka.src.Network.DeviceCard import DeviceCard
from PyAsoka.src.Core.Signal import Signal, Qt
from PyAsoka.src.Core.Object import Object
from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.Asoka import Asoka

from threading import Thread
import time


class Listener(Object):
    detected = Signal(Connection, SocketMessage)

    def __init__(self, header, callback):
        super().__init__()
        self.header = header
        self.callback = callback
        self.detected.connect(callback, Qt.ConnectionType.QueuedConnection)


class Events(Object):
    connected = Signal()
    disconnected = Signal()

    def __init__(self):
        super().__init__()


class ClientSocket(Socket):
    def __init__(self, host, port):
        super().__init__()
        self._target_address_ = (host, port)
        self._server_card_ = DeviceCard()
        self._connected_ = False
        self._events_ = Events()
        self.listeners = {}
        self.readThread = Thread()
        self.connectThread = Thread()

        self.connectToServer()

    @property
    def events(self):
        return self._events_

    @property
    def connected(self):
        return self._connected_

    def isInternetConnected(self):
        from socket import create_connection
        try:
            # connect to the host -- tells us if the host is actually
            # reachable
            create_connection(("1.1.1.1", 53))
            return True
        except OSError:
            pass
        return False

    def connectToServer(self):
        self.connectThread = Thread(target=self.__connect_to_server__)
        self.connectThread.start()

    def __connect_to_server__(self):
        from socket import socket
        host, port = self._target_address_
        self._socket_ = socket()
        while True:
            Logs.message(f'Попытка соединения с {host}:{port} ...')
            if self.isInternetConnected():
                try:
                    self.connect(host, port)
                    myKey = self.createKey()
                    print(myKey)
                    self.send('Authorization', {'deviceCard': DeviceCard.fromThisDevice().toDict(), 'key': myKey})
                    message = self.readFromConnection(self.socket)
                    if not isinstance(message, bool) and message.header == 'Authorized':
                        Logs.message(f'Соединение с сервером установлено')
                        self._connected_ = True
                        self.events.connected.emit()
                        self._server_card_ = DeviceCard.fromDict(message.json['deviceCard'])
                        serverKey = message.json['key']
                        self.setSecret(serverKey + myKey)
                        self.listenServer()
                        break
                    else:
                        Logs.message(f'Авторизация не удалась')
                except Exception as e:
                    pass
            else:
                Logs.message(f'Нет соединения с интернетом')
            time.sleep(5)

    def listenServer(self):
        self.readThread = Thread(target=self.__listen_server__)
        self.readThread.start()

    def __listen_server__(self):
        while True:
            message = self.readFromConnection(self)

            if message is None:
                continue

            elif not message:
                self.socket.close()
                Logs.message(f'Соединение с сервером разорвано')
                self._connected_ = False
                self.events.disconnected.emit()
                self.setSecret(None)
                self.connectToServer()
                break

            else:
                listener = self.listeners.get(message.header)
                if listener is not None:
                    listener.callback(self.socket, message)
                    Logs.message(f'Получено сообщение с заголовком <{message.header}>')
                else:
                    Logs.warning(f'Не распознан заголовок <{message.header}>')

            time.sleep(Asoka.defaultCycleDelay)

    def addListener(self, header, callback):
        self.listeners[header] = Listener(header, callback)
