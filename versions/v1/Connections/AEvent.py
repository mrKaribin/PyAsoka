from enum import Enum, auto


class ConnectionIntent:
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def exec(self):
        self.func(self.args)


class AEvent:
    class Type(Enum):
        CUSTOM = auto()
        SYSTEM = auto()
        UI = auto()
        AI = auto()

    def __init__(self, name: str = 'custom_event', type: Type = Type.CUSTOM):
        from PyAsoka.Id import Id

        self.id = Id()
        # print(f'New event with id = {self.id()}')
        self.name = name
        self.type = type

    def __call__(self, *args, **kwargs):
        from PyAsoka.Processing.AProcess import AProcess
        AProcess.current_process.connect_to(self.id, args, kwargs)

    def connect(self, slot, _type=None, call_type=None):
        from PyAsoka import asoka as a
        from PyAsoka.Connections.AConnector import AConnector
        a.connect(self, slot, call_type=call_type)
        return self

    def disconnect(self):
        from PyAsoka import asoka as a
        a.disconnect(self.id, None)

