from PyAsoka.GUI.Widgets.AWidget import AWidget, QPaintEvent, Styles, QPainter, QColor, QRect, QPoint

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QResizeEvent, QPainterPath


class AImageView(AWidget):
    def __init__(self, image, parent=None, **kwargs):
        AWidget.__init__(self, parent=parent, **kwargs)
        self.image = QPixmap(image)

    def paintEvent(self, event: QPaintEvent):
        if self.__is_content_visible__():
            painter = self.__get_painter__()
            painter.setCompositionMode(painter.CompositionMode_SourceOver)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setOpacity(self.alpha)
            painter.drawPixmap(0, 0, self.width(), self.height(), self.image, 0, 0, self.image.width(), self.image.height())

    def resizeEvent(self, event: QResizeEvent):
        self.image = self.image.scaled(event.size().width(), event.size().height())
