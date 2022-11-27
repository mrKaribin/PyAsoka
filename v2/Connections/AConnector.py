from PyAsoka.Connections.AEvent import AEvent
from enum import Enum, auto


class AConnector:
    class Type(Enum):
        DEFAULT = auto()
        DISPOSABLE = auto()

    class CallbackType(Enum):
        DEFAULT = auto()
        GUI = auto()

    def __init__(self, callback, process_name: str = None, call_type=None, _type=None):
        from PyAsoka.Processing.AProcess import AProcess
        from PyAsoka.Id import Id

        if _type is None:
            _type = AConnector.Type.DEFAULT
        if call_type is None:
            call_type = AConnector.CallbackType.DEFAULT

        self.id = Id(self)
        self.callback = callback
        self.type = _type
        self.call_type = call_type
        if process_name is None:
            if AProcess.current_process is not None:
                self.process_name = AProcess.current_process.name
            else:
                raise Exception('AProcess is not initialized in current process')
        AProcess.current_process.connectors.add(self)

    def __happened__(self, args, kwargs):
        from PyAsoka.Processing.AProcess import AProcess
        if self.call_type == AConnector.CallbackType.GUI:
            AProcess.current_process.gui_connect(self.callback, args, kwargs)
        else:
            if len(args) > 0 or len(kwargs) > 0:
                self.callback(*args, **kwargs)
            else:
                self.callback()

    def __del__(self):
        pass  # ToDo
