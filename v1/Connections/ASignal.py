from PySide6.QtCore import QObject
from PySide6.QtCore import Signal as QSignal

counter = 0


def call(self, *args, **kwargs):
    self.signal.emit(*args, **kwargs)


def bind(self, emiter):
    self.signal.connect(emiter)
    return self


def ASignal(*types, **kwtypes):
    global counter
    counter += 1
    signal = type(f"ASignal{counter}", (QObject, ), {'signal': QSignal(*types, **kwtypes), '__call__': call, 'bind': bind})
    return signal()
