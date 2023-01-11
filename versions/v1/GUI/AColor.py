from PySide6.QtGui import QColor
from PySide6.QtCore import QObject, Property
from PyAsoka.src.Core.Signal import Signal


class AColor(QColor, QObject):
    def __init__(self, r=0, g=0, b=0, a=255):
        super().__init__()
        QObject.__init__(self, None)

        self.changed = Signal()

        if isinstance(r, QColor) or isinstance(r, AColor):
            color = r
            self.__set_color__(color)
        else:
            self.setRgb(r, g, b, a)

    def toStyleSheet(self):
        return f'rgba({self.red()}, {self.green()}, {self.blue()}, {self.alpha()})'

    def __set_color__(self, color: QColor):
        self.setRed(color.red())
        self.setGreen(color.green())
        self.setBlue(color.blue())
        self.setAlpha(color.alpha())
        self.changed()
        return self

    def __get_color__(self):
        return QColor(self.red(), self.green(), self.blue(), self.alpha())

    color = Property(QColor, __get_color__, __set_color__)
