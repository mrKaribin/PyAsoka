from PyAsoka.Processing.AProcess import ProcessCutaway, ProcessMessage, Headers
from PyAsoka.Database.SqLite import SqLite, DatabaseProfile, DatabaseType


class DatabaseManager:
    def __init__(self):
        self.queue = []
        self.busy = False
        self.profile = DatabaseProfile(DatabaseType.SQLITE, 'lotos.db')  # not correct ToDo

    def addRequest(self, process: ProcessCutaway):
        self.queue.append(process)

    def free(self):
        self.busy = False
        if len(self.queue):
            self.exec()

    def empty(self):
        return len(self.queue) == 0

    def exec(self):
        if not self.busy and len(self.queue):
            process = self.queue.pop(0)
            SqLite.init()
            # process.channel.send(ProcessMessage(Header.DATABASE_TAKE, SqLite.))
