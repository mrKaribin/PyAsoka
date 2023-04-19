from PyAsoka.src.Core.Signal import Signal
from PySide6.QtCore import QPropertyAnimation


class Animation(QPropertyAnimation):

    def __init__(self, target, prop: bytes, start_value=None, end_value=None, duration=1000, parent=None):
        super().__init__(target, prop, parent)
        from PyAsoka.src.GUI.Style.Color import Color

        if start_value is not None:
            if isinstance(start_value, Color):
                start_value = start_value.toQColor()
            self.setStartValue(start_value)
        if end_value is not None:
            if isinstance(end_value, Color):
                end_value = end_value.toQColor()
            self.setEndValue(end_value)
        self.setDuration(duration)

    def timeRemaining(self):
        return self.duration() - self.currentLoopTime()
