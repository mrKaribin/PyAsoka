from enum import Enum, auto
from PySide6.QtCore import QPropertyAnimation, QParallelAnimationGroup

from PyAsoka.src.Core.Signal import Signal


class Animation(QPropertyAnimation):
    class Type(Enum):
        QUEUE = auto()
        PARALLEL = auto()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ended = Signal(Animation)
        self.finished.connect(lambda: self.ended(self))

        group = QParallelAnimationGroup(self)
        group.animationAt(0).prop

    def timeRemaining(self):
        return self.duration() - self.currentLoopTime()
