from PyAsoka.src.Network.Socket.Socket import Socket
from PyAsoka.src.Network.Socket.Message import SocketMessage
from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.Asoka import Asoka

from threading import Thread
import time


class ClientSocket(Socket):
    def __init__(self, host, port):
        super().__init__()
        self._target_address_ = (host, port)
        Logs.message(f'Попытка соединения с {host}:{port}')
        self.connect(host, port)

        self.readThread = Thread(target=self.run)
        self.readThread.start()

    def run(self):
        while True:
            message = self.readFromConnection(self.socket)

            if message is None:
                time.sleep(Asoka.defaultCycleDelay)
                continue

            elif not message:
                self.socket.close()
                Logs.message(f'Соединение разорвано: {self.socket.address}')

            else:
                print(message.header)
