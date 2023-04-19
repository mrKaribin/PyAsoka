from PyAsoka.src.GUI.Widget.Widget import Widget, QPaintEvent, Styles, QPainter, QColor, QRect, QPoint, QPen, Qt

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QResizeEvent, QPainterPath


class IconView(Widget):
    def __init__(self, image, frame: int = False, style=None, **kwargs):
        if style is None:
            style = Styles.Window
        super().__init__(style=style, **kwargs)
        self.image = QPixmap()
        self.is_frame = frame is not False
        self.frame_thickness = 0 if frame is None else frame
        self.setImage(image)

    def setImage(self, image):
        if isinstance(image, str):
            self.image = QPixmap(image)
        if isinstance(image, QPixmap):
            self.image = image

    def paintEvent(self, event: QPaintEvent):
        painter = self.__get_painter__()
        painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceOver)
        painter.setOpacity(self.alpha)
        radius = QPoint(self.width() // 2, self.height() // 2)
        indent = self.frame_thickness // 2

        if self.is_frame:
            painter.setPen(QPen(self.style.current.frame, indent * 2))
            painter.drawEllipse(QRect(indent, indent, self.width() - (indent * 2), self.height() - (indent * 2)))
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), radius.x(), radius.y())
        painter.setClipPath(path)
        painter.drawPixmap(indent * 3, indent * 3, self.width() - (indent * 6), self.height() - (indent * 6),
                           self.image, 0, 0, self.image.width(), self.image.height())

    def resizeEvent(self, event: QResizeEvent):
        self.image = self.image.scaled(event.size().width(),
                                       event.size().height(),
                                       Qt.AspectRatioMode.IgnoreAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
