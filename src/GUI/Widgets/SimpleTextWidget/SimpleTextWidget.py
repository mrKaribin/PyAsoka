from PyAsoka.src.Debug.Exceptions import Exceptions
from PyAsoka.src.GUI.Widget.Widget import Widget, QPainter, Props, QPaintEvent, QRect, QSize, QPoint, Color, Signal
from PyAsoka.src.GUI.Widgets.IconView import IconView
from PyAsoka.src.GUI.Widget.State import State
from PyAsoka.src.GUI.Widget.Layer import Layer
from PyAsoka.src.GUI.Style.Styles import Styles
from PyAsoka.src.GUI.Font import Font
from PyAsoka.Asoka import Asoka

from PyAsoka.src.GUI.Widgets.SimpleTextWidget.TextCursor import TextProperties, TextCursor

from PySide6.QtGui import QKeyEvent, QFontMetrics


class SimpleTextWidget(Widget):
    TextWeight = Font.Weight
    Visualization = TextProperties.Visualization

    enterEvent = Signal(str)

    def __init__(self, label: str = '',
                 flags=Asoka.Alignment.AlignLeft,
                 font: Font = None,
                 visualization: TextProperties.Visualization = TextProperties.Visualization.DEFAULT,
                 indent: tuple = (10, 10, 10, 10),
                 editable: bool = False,
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
                else:
                    self.text.cursor.insert('\n')

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
            metric = QFontMetrics(text.font)
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceOver)

            if not text.isEmpty():
                paragraphs, cursorPos = self.getTextScheme(widget, text, cursor, metric)
                self.drawString(widget, painter, text, metric, paragraphs)

            elif text.label != '':
                cursorPos = QPoint(0, 0)
                self.drawLabel(widget, painter, text, metric)

            if widget.editable and widget.hasFocus():
                self.drawCursor(widget, painter, text, metric, cursorPos)

        def getTextScheme(self, widget: Widget, text: TextProperties, cursor: TextCursor, metric: QFontMetrics):
            paragraphs = []
            spacing = 5
            lineNumber, startSymbolNum, endSymbolNum = 0, 0, 0
            cursorPos = QPoint(0, 0)
            size = QSize(widget.width() - text.indent.left - text.indent.right,
                         widget.height() - text.indent.top - text.indent.bottom)

            for paragraph in text.format().split('\n'):
                lines = []
                line = ''
                words = paragraph.split(' ')
                while len(words) > 0:
                    word = words.pop(0)
                    test_line = line + word + ' '
                    lineWidth = metric.boundingRect(test_line).width()

                    if lineWidth <= size.width():
                        line = test_line

                    if lineWidth > size.width() or len(words) == 0:
                        endSymbolNum = startSymbolNum + len(line) - 1
                        if startSymbolNum <= cursor.position <= endSymbolNum:
                            fragment = line[:cursor.position - startSymbolNum]
                            rect = metric.boundingRect(fragment)
                            cursorPos = QPoint(rect.width(), lineNumber * metric.height() + lineNumber * spacing)

                        lines.append(line[:len(line) - 1])
                        lineNumber += 1
                        line = word + ' '

                        startSymbolNum += len(line) - 1

                if len(lines) == 0:
                    lines.append('')
                    lineNumber += 1

                paragraphs.append(lines)
                startSymbolNum += 1

            return paragraphs, cursorPos

        def drawString(self, widget, painter, text, metric, paragraphs):
            spacing = 5
            indent = text.indent
            y = text.indent.top
            for paragraph in paragraphs:
                for line in paragraph:
                    # print(string)
                    met = metric.boundingRect(line)
                    rect = QRect(indent.left, y, met.width(), met.height())
                    painter.setPen(widget.style.current.text)
                    painter.setFont(text.font)
                    painter.drawText(rect, text.flags(), line)
                    y += metric.height() + spacing

        def drawLabel(self, widget, painter, text, metric):
            label = text.label
            painter.setPen(Color(255, 255, 255, 80))
            met = metric.boundingRect(label)
            rect = QRect(text.indent.left, text.indent.top, met.width() + 2, met.height())
            painter.setFont(text.font)
            painter.drawText(rect, text.flags(), label)

        def drawCursor(self, widget: Widget, painter: QPainter, text: TextProperties, metrics: QFontMetrics, position: QPoint):
            painter.drawLine(text.indent.left + position.x(), text.indent.top + position.y(),
                             text.indent.left + position.x(), text.indent.top + position.y() + metrics.height())
