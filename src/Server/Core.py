from PyAsoka.src.Network.Socket.Server import ServerSocket


class Core:
    def __init__(self):
        self.server = ServerSocket('', 12550)

    def run(self):
        pass

