from PyAsoka.src.Network.Socket.Socket import Socket
from PyAsoka.src.Network.Socket.Connection import Connection
from PyAsoka.src.Network.DeviceCard import DeviceCard
from PyAsoka.src.Core.Signal import Signal
from PyAsoka.src.Debug.Logs import Logs

from threading import Thread


class ServerSocket(Socket):
    accepted = Signal()

    def __init__(self, host, port, queue_size=10):
        super().__init__()
        self.connections = []
        self.users = {}
        self.bind(host, port)
        self.listen(queue_size)
        Logs.message(f'Запущен TCP сервер: {host}:{port}')

        self.auth_thread = Thread(target=self.authorization)
        self.auth_thread.start()
        self.server_thread = Thread(target=self.run)
        self.server_thread.start()

    def authorization(self):
        Logs.message(f'Сервер ожидает подключений')
        while True:
            connection, address = self.socket.accept()

            try:
                message = self.readFromConnection(connection)
                print(message.json['deviceCard'])
                if message.header == 'Authorization':
                    card = DeviceCard.fromJson(message.json['deviceCard'])
                    connection = Connection(connection, address, card)
                    self.connections.append(connection)
                    Logs.message(f'Новое соединение: {address}')
                    connection.send('Greetings', {'deviceCard': DeviceCard.fromThisDevice().toJson()})

            except Exception as e:
                print(e)
                connection.close()
                Logs.message(f'Авторизация не удалась: {address}')

    def run(self):
        while True:
            for connection in self.connections:
                message = self.readFromConnection(connection)

                if message is None:
                    continue

                elif not message:
                    connection.close()
                    self.connections.remove(connection)
                    Logs.message(f'Соединение разорвано: {connection.address}')

                else:
                    print(message.header)

