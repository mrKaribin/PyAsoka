from PyAsoka.Connections.AConnector import AConnector


class ConnectorsManager:
    def __init__(self):
        self.all = []

    def add(self, connector: AConnector):
        self.all.append(connector)

    def remove(self, value):
        if isinstance(value, AConnector):
            try:
                self.all.remove(value)
            except Exception as e:
                Log.warning(f"Ошибка удаления коннектора (id = {value._id_}) из менеджера. Коннектор не найден.")

        elif isinstance(value, int):
            id = value
            for c in self.all:
                if c._id_ == id:
                    self.all.remove(c)
                    return
            Log.warning(f"Ошибка удаления коннектора (id = {id}) из менеджера. Коннектор не найден.")

        else:
            raise Exception('Broken type of "value" in ConnectorsManager.remove(value)')

    def find(self, id):
        for c in self.all:
            if c._id_ == id:
                return c
        return None


class ConnectorsProcessManager(ConnectorsManager):
    def add(self, connector: AConnector):
        super(ConnectorsProcessManager, self).add(connector)
        from PyAsoka.Processing.AProcess import AProcess, ProcessMessage, Headers
        AProcess.current_process.core.channel.send(ProcessMessage(Headers.CONNECTOR_ADDED, (connector._id_._id_, connector._id_.__unique_name__)))

    def remove(self, value):
        super(ConnectorsProcessManager, self).remove(value)
        from PyAsoka.Processing.AProcess import AProcess, ProcessMessage, Headers
        id = None
        if isinstance(value, AConnector):
            id = value._id_
        elif isinstance(value, int):
            id = value
        AProcess.current_process.core.channel.send(ProcessMessage(Headers.CONNECTOR_REMOVED, (id.__id__, id.__unique_name__)))


class ConnectorsCoreManager(ConnectorsManager):
    def add(self, connector: AConnector):
        super(ConnectorsCoreManager, self).add(connector)
        from PyAsoka.Core.ACore import ACore
        from PyAsoka.Processing.AProcess import ProcessCutaway
        ACore.current_process.multi_connectors.add(connector._id_, ProcessCutaway(ACore.current_process.name, None))

    def remove(self, value):
        super(ConnectorsCoreManager, self).remove(value)
        from PyAsoka.Core.ACore import ACore
        from PyAsoka.Processing.AProcess import ProcessCutaway
        id = None
        if isinstance(value, AConnector):
            id = value._id_
        elif isinstance(value, int):
            id = value
        ACore.current_process.multi_connectors.add(id, ProcessCutaway(ACore.current_process.name, None))
