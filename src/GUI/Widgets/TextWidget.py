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


class CursorPosition:
    def __init__(self, paragraph: int, line: int, symbol: int):
        self.paragraph = paragraph
        self.line = line
        self.symbol = symbol


class Indent:
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom


class TextCursor:
    def __init__(self, text_props):
        self._text_ = text_props
        self._position_ = CursorPosition(0, 0, 0)
        self._geometry_ = QRect(0, 0, 0, 0)

    @property
    def text(self):
        return self._text_

    @property
    def position(self) -> CursorPosition:
        return self._position_

    @position.setter
    def position(self, paragraph: int = None, line: int = None, symbol: int = None):
        if paragraph is None:
            paragraph = self.position.paragraph
        if line is None:
            line = self.position.line
        if symbol is None:
            symbol = self.position.symbol

        if isinstance(paragraph, int) and isinstance(line, int) and isinstance(symbol, int):
            if 0 <= paragraph <= len(self._text_.para):
                self._position_.paragraph = paragraph
                self._position_.line = line
                self._position_.symbol = symbol
        else:
            Exceptions.UnsupportableType(paragraph, line, symbol)

    def isMin(self):
        return self.position.paragraph == 0 and self.position.line == 0 and self.position.symbol == 0

    def isMax(self):
        return self.position.paragraph == len(self.text.paragraphs) - 1 and \
            self.position.line == len(self.text.paragraphs[self.position.line]) - 1 and \
            self.position.symbol == len(self.currentLine())

    def print(self):
        print(self.position.paragraph, self.position.line, self.position.symbol)

    def currentLine(self):
        return self.text.paragraphs[self.position.paragraph][self.position.line]

    def currentParagraph(self):
        return self.text.paragraphs[self.position.paragraph]

    def insert(self, text: str):
        if isinstance(text, str):
            line = self.currentLine()
            line = line[:self.position.symbol] + text + line[self.position.symbol:]
            self.text.paragraphs[self.position.paragraph][self.position.line] = line
            self.move(len(text))
        else:
            Exceptions.UnsupportableType(text)

    def backspace(self):
        if self.position.symbol > 0:
            line = self.currentLine()
            line = line[:self.position.symbol - 1] + line[self.position.symbol:]
            self.text.paragraphs[self.position.paragraph][self.position.line] = line
            self.move(-1)
        else:
            if self.position.line > 0:
                self.position.line -= 1
                self.position.symbol = len(self.currentLine())
                self.backspace()
            else:
                if self.position.paragraph > 0:
                    self.position.paragraph -= 1
                    self.text.paragraphs.pop(self.position.paragraph + 1)
                    self.position.line = len(self.currentParagraph()) - 1
                    self.position.symbol = len(self.currentLine())
                    self.backspace()
                else:
                    return

    def delete(self):
        if self.position.symbol < len(self.currentLine()):
            line = self.currentLine()
            line = line[:self.position.symbol] + line[self.position.symbol + 1:]
            self.text.paragraphs[self.position.paragraph][self.position.line] = line

    def move(self, value: int):
        if isinstance(value, int):
            line = self.currentLine()
            if self.position.symbol + value > len(line):
                if self.position.line + 1 < len(self.currentParagraph()):
                    value = value - (len(line) - self.position.symbol)
                    self.position.symbol = 0
                    self.position.line += 1
                    self.move(value)
                    return
                elif self.position.paragraph + 1 < len(self.text.paragraphs):
                    value = value - (len(line) - self.position.symbol)
                    self.position.symbol = 0
                    self.position.line = 0
                    self.position.paragraph += 1
                    self.move(value)
                else:
                    self.position.symbol = len(line)
            elif self.position.symbol + value < 0:
                if self.position.line > 0:
                    value = value - self.position.symbol
                    self.position.line -= 1
                    self.position.symbol = len(self.currentLine())
                    self.move(value)
                elif self.position.paragraph > 0:
                    value = value - self.position.symbol
                    self.position.paragraph -= 1
                    self.position.line = len(self.text.paragraphs[self.position.paragraph]) - 1
                    self.position.symbol = len(self.currentLine())
                    self.move(value)
                else:
                    self.position.symbol = 0
            else:
                self.position.symbol += value

        else:
            Exceptions.UnsupportableType(value)

    def updateGeometry(self):
        widget = self._text_._widget_
        text = self._text_
        cursor = text.cursor
        metric = QFontMetrics(text.font)
        vertIndent = (widget.height() - metric.height()) // 2
        # rect = QRect(text.indent, vertIndent, metric.boundingRect(text.string).width(), widget.height() - vertIndent * 2)
        if text.wordWrap:
            pass
        else:
            leftWidth = metric.boundingRect(text.cursor.currentLine()[:cursor.position.symbol]).width()
            if leftWidth - text.shift.width() + text.indent.left * 2 > widget.width():
                text.shift.setWidth(leftWidth - widget.width() + text.indent.left * 2)
            elif leftWidth < text.shift.width():
                text.shift.setWidth(leftWidth)
        widget.repaint()


class TextProperties:
    class Visualization(IntEnum):
        DEFAULT = 1
        SECRET = 2

    def __init__(self, widget: Widget,
                 label: str = '',
                 flags=Asoka.Alignment.AlignLeft | Asoka.TextFlag.TextSingleLine,
                 font: Font = Font("Times", 10, Font.Weight.Normal, False),
                 visualization: Visualization = Visualization.DEFAULT,
                 single_line: bool = False,
                 indent: tuple = (10, 10, 10, 10)):
        self._widget_ = widget
        self._paragraphs_ = [['']]
        self._label_ = label
        self._flags_ = flags
        self._font_ = font
        self._indent_ = Indent(*indent)
        self._cursor_ = TextCursor(self)
        self._visualization_ = visualization
        self._single_line_ = single_line
        self._word_wrap_ = False
        self._shift_ = QSize(0, 0)

    @property
    def widget(self):
        return self._widget_

    @property
    def label(self):
        return self._label_

    @property
    def string(self):
        string = ''
        for i in range(len(self.paragraphs)):
            if i >= 1:
                string += '\n'
            for j in range(len(self.paragraphs[i])):
                string += self.paragraphs[i][j]
        return string

    @string.setter
    def string(self, string: str):
        if isinstance(string, str):
            metric = QFontMetrics(self.font)
            paragraphs = []
            pre_lines = string.split('\n')
            for pre_line in pre_lines:
                paragraph = []
                if self.wordWrap:
                    width = metric.boundingRect(pre_line).width()
                    if width > self.widget.width():
                        sub_line = ''
                        words = pre_line.split(pre_line)
                        for word in words:
                            sub_line += word
                            width = metric.boundingRect(sub_line).width()
                            if width > self.widget.width():
                                paragraph.append(str(sub_line))
                                sub_line = ''
                        if sub_line != '':
                            paragraph.append(str(sub_line))
                else:
                    paragraph.append(pre_line)
                paragraphs.append(paragraph)
            self._paragraphs_ = paragraphs

            lastPar = paragraphs[len(paragraphs) - 1]
            lastLineSize = lastPar[len(lastPar) - 1]
            self.cursor.position = (len(paragraphs) - 1, len(lastPar) - 1, len(lastLineSize) - 1)

            # self._string_ = string
            # self.cursor.position = len(string)
        else:
            Exceptions.UnsupportableType(string)

    @property
    def paragraphs(self):
        return self._paragraphs_

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
        return self._single_line_

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
        return self.paragraphs == [['']]

    def updateGeometry(self, string):
        metric = QFontMetrics(self.font)

    def format(self):
        if self.visualization == self.Visualization.DEFAULT:
            return self.paragraphs
        elif self.visualization == self.Visualization.SECRET:
            paragraphs = []
            for paragraph in self.paragraphs:
                par = []
                for line in paragraph:
                    ln = ''
                    for sym in line:
                        ln += '*'
                    par.append(ln)
                paragraphs.append(par)
            return paragraphs


class TextWidget(Widget):
    TextWeight = Font.Weight
    Visualization = TextProperties.Visualization

    enterEvent = Signal(str)

    def __init__(self, label: str = '',
                 flags=Asoka.Alignment.AlignLeft,
                 font: Font = Font("Times", 10, Font.Weight.Normal, False),
                 visualization: TextProperties.Visualization = TextProperties.Visualization.DEFAULT,
                 indent: tuple = (10, 10, 10, 10),
                 editable: bool = False,
                 single_line: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._text_ = TextProperties(self, label, flags, font, visualization, single_line, indent)
        self._editable_ = False

        self.layers.textArea.enable()
        self.editable = editable

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
            print(event.key(), Asoka.Key.Key_Enter, event.key() == Asoka.Key.Key_Enter)
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
                # text._string_ = text.string[:cursor.position] + event.text() + text.string[cursor.position:]
                # cursor.position += 1
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
            # string = text.format()
            label = text.label
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceOver)

            if not text.isEmpty():
                y = widget.text.indent.top
                for paragraph in widget.text.format():
                    for line in paragraph:
                        met = metric.boundingRect(line)
                        painter.setPen(widget.style.current.text)
                        rect = QRect(text.indent.left - text.shift.width(), y,
                                     met.width(), met.height())
                        painter.setFont(font)
                        painter.drawText(rect, text._flags_, line)
                        y += widget.text.indent.top // 2
                    y += widget.text.indent.top // 2
            else:
                painter.setPen(Color(255, 255, 255, 80))
                met = metric.boundingRect(label)
                rect = QRect(text.indent.left, text.indent.top, met.width(), met.height())
                painter.setFont(font)
                painter.drawText(rect, text._flags_, label)

            if widget.editable and widget.hasFocus():
                painter.setPen(Color(255, 255, 0, 255))
                if not text.isEmpty():
                    fragment = text.format()[cursor.position.paragraph][cursor.position.line][:cursor.position.symbol]
                    met = metric.boundingRect(fragment)
                    posX, height = text.indent.left + met.width() + 1, met.height()
                else:
                    fragment = 'text'
                    met = metric.boundingRect(fragment)
                    posX, height = text.indent.left + 1, met.height()
                painter.drawLine(posX, text.indent.top, posX, text.indent.top + height)
