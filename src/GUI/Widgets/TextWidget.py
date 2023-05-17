from PyAsoka.src.Debug.Exceptions import Exceptions
from PyAsoka.src.GUI.Widget.Widget import Widget, QPainter, Props, QPaintEvent, QRect, QSize, QPoint, Color, Signal
from PyAsoka.src.GUI.Widgets.IconView import IconView
from PyAsoka.src.GUI.Widget.State import State
from PyAsoka.src.GUI.Widget.Layer import Layer
from PyAsoka.src.GUI.Style.Styles import Styles
from PyAsoka.src.GUI.Font import Font
from PyAsoka.Asoka import Asoka

from PySide6.QtGui import QKeyEvent, QKeySequence, QFontMetrics

from enum import IntEnum


class Indent:
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom


class TextCursor:
    def __init__(self, text_props):
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
        pass

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


class TextProperties:
    class Visualization(IntEnum):
        DEFAULT = 1
        SECRET = 2

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
        if font is None:
            font = Font("Times", 10, Font.Weight.Normal, False)

        self._widget_ = widget
        self._label_ = label
        self._string_ = ''
        self._flags_ = TextProperties.TextFlags()
        self._font_ = font
        self._indent_ = Indent(*indent)
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


class TextWidget(Widget):
    TextWeight = Font.Weight
    Visualization = TextProperties.Visualization

    enterEvent = Signal(str)

    def __init__(self, label: str = '',
                 flags=Asoka.Alignment.AlignLeft,
                 font: Font = None,
                 visualization: TextProperties.Visualization = TextProperties.Visualization.DEFAULT,
                 indent: tuple = (10, 10, 10, 10),
                 editable: bool = False,
                 single_line: bool = False,
                 text_bold: bool = None,
                 text_size: int = None, **kwargs):
        if font is None:
            font = Font("Times", 10, Font.Weight.Normal, False)

        if 'min_size' not in kwargs.keys():
            kwargs['min_size'] = (100, 35)

        super().__init__(**kwargs)
        self._text_ = TextProperties(self, label, flags, font, visualization, indent)
        if text_bold is not None:
            self.text.font.setBold(text_bold)
        if text_size is not None:
            self.text.font.setPointSize(text_size)
        self._editable_ = editable
        self.clickable = True
        self.clicked.connect(self.setFocus)

        self.layers.textArea.enable()

    @property
    def text(self):
        return self._text_

    @property
    def editable(self):
        return self._editable_

    @editable.setter
    def editable(self, state: bool):
        if isinstance(state, bool):
            self._editable_ = state
            if state:
                self.clickable = True
                self.clicked.connect(self.setFocus)
            else:
                self.clicked.disconnect(self.setFocus)
        else:
            Exceptions.UnsupportableType(state)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        super().keyPressEvent(event)
        text = self.text
        cursor = text.cursor
        if event.text() != '':
            # print(event.key(), Asoka.Key.Key_Enter, event.key() == Asoka.Key.Key_Enter)
            if event.key() == Asoka.Key.Key_Backspace:
                self.text.cursor.backspace()
            elif event.key() == Asoka.Key.Key_Tab:
                pass
            elif event.key() == 16777220:
                if self.text.singleLine:
                    self.enterEvent.emit(self.text.string)
            elif event.key() == Asoka.Key.Key_Delete:
                if not cursor.isMax():
                    cursor.delete()
            else:
                cursor.insert(event.text())
        else:
            if event.key() == Asoka.Key.Key_Left:
                if not cursor.isMin():
                    cursor.move(-1)
            elif event.key() == Asoka.Key.Key_Right:
                if not cursor.isMax():
                    cursor.move(1)
        cursor.updateGeometry()
        self.repaint()

    class TextArea(Layer, level=Layer.Level.TOP):
        def paint(self, widget, painter: QPainter, style, props: Props, event: QPaintEvent):
            text = widget.text
            cursor = text.cursor
            font = text.font
            metric = QFontMetrics(font)
            label = text.label
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceOver)

            if not text.isEmpty():
                y = widget.text.indent.top
                string = text.format()
                met = metric.boundingRect(string)
                painter.setPen(widget.style.current.text)
                rect = QRect(text.indent.left - text.shift.width(), y,
                             met.width() + 2, met.height())
                painter.setFont(font)
                painter.drawText(rect, text.flags(), string)
                y += widget.text.indent.top // 2
            elif label != '':
                painter.setPen(Color(255, 255, 255, 80))
                met = metric.boundingRect(label)
                rect = QRect(text.indent.left, text.indent.top, met.width() + 2, met.height())
                painter.setFont(font)
                painter.drawText(rect, text.flags(), label)

            if widget.editable and widget.hasFocus():
                painter.setPen(Color(255, 255, 0, 255))
                if not text.isEmpty():
                    print(text.format(), cursor.position)
                    fragment = text.format()[:cursor.position]
                    met = metric.boundingRect(fragment)

                    posX, height = text.indent.left + met.width() + 1, met.height()
                else:
                    fragment = 'text'
                    met = metric.boundingRect(fragment)
                    posX, height = text.indent.left + 1, met.height()
                painter.drawLine(posX, text.indent.top, posX, text.indent.top + height)
