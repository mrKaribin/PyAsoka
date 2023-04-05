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


class ServerSocket(Socket):
    def __init__(self, host, port, queue_size=10):
        super().__init__()
        self.connections = []
        self.users = {}
        self.listeners = {}
        self.bind(host, port)
        self.listen(queue_size)
        self.authorizationThread = Thread()
        self.clientsThread = Thread()
        Logs.message(f'Запущен TCP сервер: {host}:{port}')

        self.authorizationClients()
        self.listenClients()

    def authorizationClients(self):
        self.authorizationThread = Thread(target=self.__authorization_clients__)
        self.authorizationThread.start()

    def __authorization_clients__(self):
        Logs.message(f'Сервер ожидает подключений')
        while True:
            connection, address = self.socket.accept()

            try:
                message = self.readFromConnection(connection)
                if not isinstance(message, bool) and message.header == 'Authorization':
                    self.connectClient(connection, address, message)
                else:
                    connection.close()
                    Logs.message(f'Соединение отклонено: {address}')

            except Exception as e:
                print(e)
                connection.close()
                Logs.message(f'Авторизация не удалась: {address}')

    def listenClients(self):
        self.clientsThread = Thread(target=self.__listen_clients__)
        self.clientsThread.start()

    def __listen_clients__(self):
        while True:
            for connection in self.connections:
                message = self.readFromConnection(connection)

                if message is None:
                    continue

                elif not message:
                    self.disconnectClient(connection)

                else:
                    listener = self.listeners.get(message.header)
                    if listener is not None:
                        listener.callback(connection, message)
                        Logs.message(f'Получено сообщение от {connection.address} с заголовком <{message.header}>')
                    else:
                        Logs.warning(f'Не распознан заголовок <{message.header}> сообщения от {connection.address}')

            time.sleep(Asoka.defaultCycleDelay)

    def connectClient(self, con, address, message):
        myKey = self.createKey()
        clientKey = message.json['key']
        connection = Connection(con, address, DeviceCard.fromDict(message.json['deviceCard']))
        connection.send('Authorized', {'deviceCard': DeviceCard.fromThisDevice().toDict(), 'key': myKey})
        connection.setSecret(myKey + clientKey)
        Logs.message(f'Новое соединение: {address}. Всего {len(self.connections) + 1} клиентов')
        self.connections.append(connection)

    def disconnectClient(self, connection):
        connection.close()
        self.connections.remove(connection)
        Logs.message(f'Соединение разорвано: {connection.address}. Всего {len(self.connections)} клиентов')

    def addListener(self, header, callback):
        self.listeners[header] = Listener(header, callback)
