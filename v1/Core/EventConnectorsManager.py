from PyAsoka.Connections.AEvent import AEvent


class EventConnector:
    def __init__(self, event_id, connector_id):
        self.event_id = event_id
        self.connectors_id = []
        self.connectors_id.append(connector_id)

    def add(self, connector_id, connector_call_type):
        self.connectors_id.append(connector_id)

    def remove(self, connector_id):
        self.connectors_id.remove(connector_id)


class EventConnectorsManager:
    def __init__(self):
        self.connectors = []

    def add(self, event_id: int, connector_id: int):
        if (connector := self.find(event_id)) is None:
            self.connectors.append(EventConnector(event_id, connector_id))
        else:
            connector.add(connector_id)

    def remove(self, event_id, connector_id=None):
        for connector in self.connectors:
            if connector.event_id == event_id:
                if connector_id is not None:
                    connector.remove(connector_id)
                else:
                    self.connectors.remove(connector)
        # print(f'Available events: {[connector.event_id for connector in self.connectors]}')

    def find(self, event_id):
        for connector in self.connectors:
            if connector.event_id == event_id:
                return connector
        return None
