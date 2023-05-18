from PyAsoka.src.GUI.Widget.Widget import Widget, QSize
from PyAsoka.src.GUI.Font import Font
from PyAsoka.src.Debug.Exceptions import Exceptions
from PyAsoka.Asoka import Asoka

from PySide6.QtGui import QFontMetrics

from enum import IntEnum


class TextProperties:
    class Visualization(IntEnum):
        DEFAULT = 1
        SECRET = 2

    class Indent:
        def __init__(self, left, right, top, bottom):
            self.left = left
            self.right = right
            self.top = top
            self.bottom = bottom

    class TextFlags:
        def __init__(self):
            self._flags_: list[Asoka.TextFlag] = []

        def __call__(self):
            value = 0
            for flag in self._flags_:
                value = value | flag
            return value

        def add(self, flag: Asoka.TextFlag):
            if not self.exists(flag):
                self._flags_.append(flag)
            return self

        def remove(self, flag: Asoka.TextFlag):
            if self.exists(flag):
                self._flags_.remove(flag)
            return self

        def exists(self, flag: Asoka.TextFlag):
            return flag is self._flags_

    def __init__(self, widget: Widget,
                 label: str = '',
                 flags=(Asoka.Alignment.AlignLeft, Asoka.TextFlag.TextSingleLine),
                 font: Font = None,
                 visualization: Visualization = Visualization.DEFAULT,
                 indent: tuple = (10, 10, 10, 10)):
        from PyAsoka.src.GUI.Widgets.SimpleTextWidget.TextCursor import TextCursor

        if font is None:
            font = Font("Times", 10, Font.Weight.Normal, False)

        self._widget_ = widget
        self._label_ = label
        self._string_ = ''
        self._flags_ = TextProperties.TextFlags()
        self._font_ = font
        self._indent_ = TextProperties.Indent(*indent)
        self._cursor_ = TextCursor(self)
        self._visualization_ = visualization
        self._word_wrap_ = False
        self._shift_ = QSize(0, 0)

        for flag in flags:
            self.flags.add(flag)

    @property
    def widget(self):
        return self._widget_

    @property
    def label(self):
        return self._label_

    @property
    def flags(self):
        return self._flags_

    @property
    def string(self):
        return self._string_

    @string.setter
    def string(self, string: str):
        if isinstance(string, str):
            self._string_ = string
            self.widget.repaint()
        else:
            Exceptions.UnsupportableType(string)

    @property
    def visualization(self):
        return self._visualization_

    @visualization.setter
    def visualization(self, visual: Visualization):
        if isinstance(visual, self.Visualization):
            self._visualization_ = visual
        else:
            Exceptions.UnsupportableType(visual)

    @property
    def font(self):
        return self._font_

    @font.setter
    def font(self, font: Font):
        if isinstance(font, Font):
            self._font_ = font
        else:
            Exceptions.UnsupportableType(font)

    @property
    def cursor(self):
        return self._cursor_

    @property
    def indent(self):
        return self._indent_

    @property
    def singleLine(self):
        return self.flags.exists(Asoka.TextFlag.TextSingleLine)

    @singleLine.setter
    def singleLine(self, state: bool):
        if isinstance(state, bool):
            if state:
                self.flags.add(Asoka.TextFlag.TextSingleLine)
            else:
                self.flags.remove(Asoka.TextFlag.TextSingleLine)
        else:
            raise Exceptions.UnsupportableType(state)

    @property
    def wordWrap(self):
        return self._word_wrap_

    @wordWrap.setter
    def wordWrap(self, state: bool):
        if isinstance(state, bool):
            self._word_wrap_ = state
        else:
            Exceptions.UnsupportableType(state)

    @property
    def shift(self):
        return self._shift_

    def isEmpty(self):
        return self.string == ''

    def updateGeometry(self, string):
        metric = QFontMetrics(self.font)

    def format(self):
        if self.visualization == self.Visualization.DEFAULT:
            return self.string
        elif self.visualization == self.Visualization.SECRET:
            result = self.string
            for sym in result:
                if sym != '\n':
                    sym = '*'
            return result
