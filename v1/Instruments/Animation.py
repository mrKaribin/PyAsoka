from enum import Enum, auto
from PySide6.QtCore import QPropertyAnimation

from PyAsoka.Connections.ASignal import ASignal


class Animation(QPropertyAnimation):
    class Type(Enum):
        QUEUE = auto()
        PARALLEL = auto()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ended = ASignal(Animation)
        self.finished.connect(lambda: self.ended(self))

    def timeRemaining(self):
        return self.duration() - self.currentLoopTime()
