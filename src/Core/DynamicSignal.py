from PySide6.QtCore import QObject
from PySide6.QtCore import Signal as QSignal, Qt

counter = 0
SignalType = Qt.ConnectionType


def call(self, *args, **kwargs):
    self.signal.emit(*args, **kwargs)


def bind(self, emitter, _type=Qt.ConnectionType.AutoConnection):
    self.signal.connect(emitter, _type)
    return self


def DynamicSignal(*types, **kwtypes):
    global counter
    counter += 1
    signal = type(f"ASignal{counter}", (QObject, ), {
        'Type': Qt.ConnectionType,
        'signal': QSignal(*types, **kwtypes),
        '__call__': call,
        'bind': bind
    })
    return signal()
