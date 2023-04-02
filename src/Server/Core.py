from PyAsoka.src.Network.Socket.Server import ServerSocket


class Core:
    def __init__(self, host, port):
        self.server = ServerSocket(host, port)

    def run(self):
        pass

