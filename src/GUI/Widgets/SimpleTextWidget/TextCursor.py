from PyAsoka.src.GUI.Widgets.SimpleTextWidget.TextProperties import TextProperties
from PyAsoka.src.GUI.Widget.Widget import QRect
from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.src.Debug.Exceptions import Exceptions

from PySide6.QtGui import QFontMetrics


class TextCursor(Object):
    positionChanged = Signal(int)

    def __init__(self, text_props):
        super().__init__()
        self._text_ = text_props
        self._position_ = 0
        self._geometry_ = QRect(0, 0, 0, 0)

    @property
    def text(self) -> 'TextProperties':
        return self._text_

    @property
    def position(self) -> int:
        return self._position_

    @position.setter
    def position(self, position: int):
        if isinstance(position, int):
            if 0 <= position <= len(self.text.string):
                self._position_ = position
                self.positionChanged.emit(position)
        else:
            Exceptions.UnsupportableType(position)

    def isMin(self):
        return self.position == 0

    def isMax(self):
        return self.position == len(self.text.string)

    def insert(self, text: str):
        if isinstance(text, str):
            self.text.string = self.text.string[:self.position] + text + self.text.string[self.position:]
            self.move(len(text))
        else:
            Exceptions.UnsupportableType(text)

    def backspace(self):
        if not self.text.isEmpty():
            self.text.string = self.text.string[:self.position - 1] + self.text.string[self.position:]
            self.text.cursor.move(-1)

    def delete(self):
        if not self.text.isEmpty():
            self.text.string = self.text.string[:self.position] + self.text.string[self.position + 1:]

    def move(self, value: int):
        if isinstance(value, int):
            self.position = self.position + value
        else:
            Exceptions.UnsupportableType(value)

    def updateGeometry(self):
        widget = self._text_._widget_
        text = self._text_
        cursor = text.cursor
        metric = QFontMetrics(text.font)
        vertIndent = (widget.height() - metric.height()) // 2

        widget.repaint()