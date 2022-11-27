

class ConnectorsCutaway:
    def __init__(self, id, process):
        self.id = id
        self.process = process


class ConnectorsMultiprocessManager:
    def __init__(self):
        self.all = []

    def add(self, id, process):
        self.all.append(ConnectorsCutaway(id, process))

    def remove(self, id):
        if (connection := self.find(id)) is not None:
            self.all.remove(connection)

    def find(self, id):
        for connection in self.all:
            if connection.id == id:
                return connection
        return None
