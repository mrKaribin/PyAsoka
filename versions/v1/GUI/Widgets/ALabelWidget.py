import math

from PyAsoka.GUI.Widgets.AWidget import AWidget, QPaintEvent, QSize

from PySide6.QtGui import QResizeEvent, QPalette, QFontMetrics
from PySide6.QtCore import Qt


class ALabelWidget(AWidget):
    def __init__(self, label_type, text: str = '', text_size: int = 10, alignment: Qt.Alignment = Qt.AlignLeft, **kwargs):
        super().__init__(**kwargs)

        self._indent_ = 10
        self._label_ = label_type(self)
        self._label_.setGeometry(self._indent_, self._indent_, self.width() - self._indent_, self.height() - self._indent_)

        from PySide6.QtWidgets import QLabel
        self.setText(text)
        self.setTextSize(text_size)
        self.setAlignment(alignment)
        self.setMinimumSize(self.adjustSize())

    def paintEvent(self, event: QPaintEvent):
        if self.__is_content_visible__():
            super().paintEvent(event)

    def resizeEvent(self, event: QResizeEvent):
        self._label_.resize(event.size().width() - self._indent_ * 2, event.size().height() - self._indent_ * 2)

    def adjustSize(self):
        metrics = QFontMetrics(self._label_.font())
        size = QSize(metrics.horizontalAdvance(self._label_.text()), metrics.height())
        max_width = self.maximumWidth() - self._indent_ * 2
        if size.width() > max_width:
            size = QSize(max_width - self._indent_ * 2, math.ceil(size.width() / max_width) * size.height())
        size = QSize(size.width() + self._indent_ * 2, size.height() + self._indent_ * 2)
        return size

    def setAlignment(self, alignment: Qt.Alignment):
        self._label_.setAlignment(alignment)

    def setText(self, text: str = ''):
        self._label_.setText(text)

    def setTextSize(self, size: int):
        font = self._label_.font()
        font.setPointSize(size)
        self._label_.setFont(font)

    def setTextBold(self, value: bool):
        font = self._label_.font()
        font.setBold(value)
        self._label_.setFont(font)

    def getText(self):
        return self._label_.getText()

    def getTextSize(self):
        return self._label_.font().pointSize()

    def __update_palette__(self):
        pass
