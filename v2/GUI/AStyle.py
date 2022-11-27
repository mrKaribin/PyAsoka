from PySide6.QtCore import QObject
from PySide6.QtGui import QColor
from PyAsoka.Connections.ASignal import ASignal
from PyAsoka.GUI.AColor import AColor


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
            self.background = AColor(style.background) if style.background is not None else None
            self.background_line = AColor(style.background_line) if style.background_line is not None else None
            self.frame = AColor(style.frame) if style.frame is not None else None
            self.line = AColor(style.line) if style.line is not None else None
            self.text = AColor(style.text) if style.text is not None else None

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

        self.changed = ASignal()
