from enum import Enum, auto

from PyAsoka.Connections.AConnector import AConnector, AEvent
from PyAsoka.Core.Linguistics.APhraseModel import APhraseModel


class AActionPrototype:
    class Type(Enum):
        MOMENTARY = auto()
        CONTINUOUS = auto()

    def __init__(self):
        pass

    def delete(self):
        pass


class AFunctionAction(AActionPrototype):
    def __init__(self, model: APhraseModel, function, _type=None, call_type=AConnector.CallbackType.DEFAULT):
        super().__init__()
        from PyAsoka.Core.ACore import ACore, AProcess, ProcessMessage, Headers
        if _type is None:
            _type = AFunctionAction.Type.MOMENTARY

        self.model = model
        self.event = AEvent(type=AEvent.Type.SYSTEM).connect(function, call_type=call_type)
        self.type = _type

        process = AProcess.current_process
        if process.name != 'CoreProcess':
            process.core.channel.send(ProcessMessage(Headers.ACTION_ADD, (self.model, self.type, self.event.id)))
        else:
            process.add_action(self.model, self.event.id, _type)

    def delete(self):
        from PyAsoka.Core.ACore import AProcess, ProcessMessage, Headers
        self.event.disconnect()
        process = AProcess.current_process
        if process.name != 'CoreProcess':
            process.core.channel.send(ProcessMessage(Headers.ACTION_REMOVE, self.event.id))
        else:
            process.remove_action(self.model)

    def __del__(self):
        self.delete()
