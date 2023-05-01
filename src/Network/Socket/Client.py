from PyAsoka.src.Network.Socket.Socket import Socket
from PyAsoka.src.Network.Socket.Connection import Connection
from PyAsoka.src.Network.Socket.Message import SocketMessage
from PyAsoka.src.Network.DeviceCard import DeviceCard
from PyAsoka.src.Instruments.Timepoint import Timepoint
from PyAsoka.src.Core.Signal import Signal, Qt
from PyAsoka.src.Core.Object import Object
from PyAsoka.src.Debug.Logs import Logs

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
        self._listeners_ = {}
        self._requests_ = []
        self._readThread_ = Thread()
        self._connectThread_ = Thread()

        self.connectToServer()

    @property
    def events(self):
        return self._events_

    @property
    def connected(self):
        return self._connected_

    def waitForConnection(self):
        from PyAsoka.Asoka import Asoka
        while not self.connected:
            time.sleep(Asoka.defaultCycleDelay)

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
        self._connectThread_ = Thread(target=self.__connect_to_server__)
        self._connectThread_.start()

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
                    # print(myKey)
                    self.send('Authorization', {'deviceCard': DeviceCard.fromThisDevice().toDict(), 'key': myKey})
                    message = self.readFromConnection(self.socket)
                    if not isinstance(message, bool) and message.header == 'Authorized':
                        Logs.message(f'Соединение с сервером установлено')
                        self._connected_ = True
                        self.events.connected.emit()
                        self._server_card_ = DeviceCard.fromDict(message.json['deviceCard'])
                        serverKey = message.json['key']
                        # self.setSecret(serverKey + myKey)
                        self.listenServer()
                        break
                    else:
                        self.close()
                        Logs.message(f'Авторизация не удалась')
                except Exception as e:
                    print(e)
                    pass
            else:
                Logs.message(f'Нет соединения с интернетом')
            time.sleep(5)

    def listenServer(self):
        self._readThread_ = Thread(target=self.__listen_server__)
        self._readThread_.start()

    def __listen_server__(self):
        from PyAsoka.Asoka import Asoka
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
                listener = self._listeners_.get(message.header)
                request = self.findRequest(message)
                if listener is not None:
                    listener.callback(self.socket, message)
                    Logs.message(f'Получено сообщение с заголовком <{message.header}>')
                elif request is not None:
                    request['reply'] = message
                else:
                    Logs.warning(f'Не распознан заголовок <{message.header}>')

            time.sleep(Asoka.defaultCycleDelay)

    def generateRequestKey(self):
        from PyAsoka.Asoka import Asoka
        ok = False
        key = ''
        while not ok:
            key = Asoka.Generate.Key.hybrid()
            for request in self._requests_:
                if request['key'] == key:
                    continue
            ok = True
        return key

    def findRequest(self, message: SocketMessage):
        if message.isRequest():
            key = message.json['request']['key']
            for request in self._requests_:
                if request['header'] == message.header and request['key'] == key:
                    return request
        return None

    def addListener(self, header, callback):
        self._listeners_[header] = Listener(header, callback)

    def request(self, header: str, data: dict = None, reply_header: str = None) -> SocketMessage:
        from PyAsoka.Asoka import Asoka
        if reply_header is None:
            reply_header = header + 'Reply'
        if data is None:
            data = {}

        request = {
            'header': reply_header,
            'key': self.generateRequestKey(),
            'time': Timepoint.now().toDict()
        }
        data['request'] = request
        self.send(header, data)

        request['reply'] = False
        self._requests_.append(request)

        while not request['reply']:
            time.sleep(Asoka.defaultCycleDelay)

        self._requests_.remove(request)
        return request['reply']
