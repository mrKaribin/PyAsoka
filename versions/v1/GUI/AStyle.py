from PySide6.QtCore import QObject
from PySide6.QtGui import QColor
from PyAsoka.Connections.Signal import Signal
from PyAsoka.GUI.Color import Color


class AStyle:
    def __init__(self, style: QObject = None,
                 background=None,
                 background_line=None,
                 frame=None,
                 line=None,
                 text=None):
        if style is None:
            self.background = background
            self.background_line = background_line
            self.frame = frame
            self.line = line
            self.text = text
        else:
            self.background = Color(style.background) if style.background is not None else None
            self.background_line = Color(style.background_line) if style.background_line is not None else None
            self.frame = Color(style.frame) if style.frame is not None else None
            self.line = Color(style.line) if style.line is not None else None
            self.text = Color(style.text) if style.text is not None else None

        if self.background is not None:
            self.background.changed.bind(lambda: self.changed())
        if self.background_line is not None:
            self.background_line.changed.bind(lambda: self.changed())
        if self.frame is not None:
            self.frame.changed.bind(lambda: self.changed())
        if self.line is not None:
            self.line.changed.bind(lambda: self.changed())
        if self.text is not None:
            self.text.changed.bind(lambda: self.changed())

        self.changed = Signal()
