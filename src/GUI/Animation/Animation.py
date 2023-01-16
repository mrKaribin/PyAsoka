from PyAsoka.src.Core.Signal import Signal
from PySide6.QtCore import QPropertyAnimation


class Animation(QPropertyAnimation):

    def __init__(self, target, prop: bytes, start_value=None, end_value=None, duration=1000, parent=None):
        super().__init__(target, prop, parent)
        if start_value is not None:
            self.setStartValue(start_value)
        if end_value is not None:
            self.setEndValue(end_value)
        self.setDuration(duration)

    def timeRemaining(self):
        return self.duration() - self.currentLoopTime()
