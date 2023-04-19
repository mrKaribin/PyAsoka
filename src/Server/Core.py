from PyAsoka.src.Network.Socket.Server import ServerSocket


class Core:
    current = None

    def __init__(self, host, port):
        Core.current = self
        self._server_ = ServerSocket(host, port)

    @property
    def server(self):
        return self._server_

    def addServerListener(self, header, callback):
        self.server.addListener(header, callback)

    def run(self):
        pass


def core() -> Core:
    return Core.current
