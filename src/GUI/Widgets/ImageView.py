from PyAsoka.src.GUI.Widget.Widget import Widget, QPaintEvent, Styles, QPainter, QColor, QRect, QPoint, Qt, Color, QPen

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QResizeEvent, QPainterPath


class ImageView(Widget):
    def __init__(self, image, image_size=None, **kwargs):
        super(ImageView, self).__init__(**kwargs)

        self.image = QPixmap(image)
        if image_size is not None:
            width, width = image_size
            self.image = self.image.scaled(width, width, mode=Qt.TransformationMode.SmoothTransformation)

    def paintEvent(self, event: QPaintEvent):
        painter = self.__get_painter__()
        painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceOver)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.alpha)
        image = self.image.scaled(self.width(), self.height(), mode=Qt.TransformationMode.SmoothTransformation)
        painter.drawPixmap(0, 0, self.width(), self.height(), image, 0, 0, image.width(), image.height())

    def resizeEvent(self, event: QResizeEvent):
        self.image = self.image.scaled(event.size().width(), event.size().height())
